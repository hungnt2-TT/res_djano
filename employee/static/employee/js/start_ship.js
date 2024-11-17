$(document).ready(function () {
    showLoading();
    console.log("Start Ship page loaded");
    $("#btn-accept-order").on("click", function () {
        console.log("Accept order button clicked");
        showLoading();
        const orderId = $(this).data("order-id");
        const url = $(this).data("url");
        const csrfToken = "{{ csrf_token }}";

        $.ajax({
            url: url,
            type: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
            },
            contentType: "application/json",
            data: JSON.stringify({order_id: orderId}),
            success: function (response) {
                if (response.success) {
                    Swal.fire({
                        icon: "success", title: "Success", text: "Start shipping successfully.",
                    });
                    hideLoading();
                    window.location.reload();
                }
            },
            error: function (xhr, status, error) {
                Swal.fire({
                    icon: "error", title: "Error", text: "Something went wrong. Please try again later.",
                });
                hideLoading();
            }
        });
    });
    $("#complete-ship-form").submit(function (e) {
        e.preventDefault();
        const proofImage = $("#proof-image")[0].files[0];
        console.log('proofImage', proofImage);

        if (!proofImage) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "Please upload the proof image.",
            });
            return;
        }
        console.log('$("#proof-image")[0].files[0]); ', $("#proof-image")[0].files[0])
        console.log('$("#order-id").val()', $("#order-id").val())
        const formData = new FormData();
        formData.append("proof_image", $("#proof-image")[0].files[0]);
        formData.append("order_id", $("#order-id").val());
        formData.append("csrfmiddlewaretoken", "{{ csrf_token }}");

        $.ajax({
            url: $(this).attr("action"),
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Success",
                        text: "Order has been completed successfully.",
                    });
                    location.reload();
                } else {
                    Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: response.message,
                        }
                    )

                }
            },
            error: function () {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: "Something went wrong. Please try again later.",
                });
            }
        });
    });

    function showLoading() {
        $("#loading_spinner").removeClass("d-none");
        $("#loadingArea").removeClass("d-none");
    }

    function hideLoading() {
        $("#loading_spinner").addClass("d-none");
        $("#loadingArea").addClass("d-none");
    }

    function getLatLng(location) {
        if (typeof location.lat === "function" && typeof location.lng === "function") {
            return {lat: location.lat(), lng: location.lng()};
        } else if (typeof location === "string") {
            const [lat, lng] = location.split(",").map(coord => parseFloat(coord.trim()));
            return {lat, lng};
        } else if (typeof location === "object" && location.lat && location.lng) {
            return location;
        } else {
            throw new Error("Invalid location format");
        }
    }

    function initMap() {
        const userLocation = $("#user_location").val();
        const shipperLocation = $("#shipper_location").val();

        const userLatLng = getLatLng(userLocation);
        const shipperLatLng = getLatLng(shipperLocation);
        const map = new google.maps.Map(document.getElementById("map"), {
            center: shipperLatLng, zoom: 5,
        });
        const shipperMarker = new google.maps.Marker({
            position: shipperLatLng, map: map, icon: {
                url: "https://maps.google.com/mapfiles/kml/shapes/motorcycling.png",
                scaledSize: new google.maps.Size(40, 40),
            }, title: "Shipper's Location",
        });

        const userMarker = new google.maps.Marker({
            position: userLatLng, map: map, icon: {
                url: "https://maps.google.com/mapfiles/kml/shapes/homegardenbusiness.png",
                scaledSize: new google.maps.Size(40, 40),
            }, title: "User's Location",
        });

        const directionsService = new google.maps.DirectionsService();
        const directionsRenderer = new google.maps.DirectionsRenderer({
            map: map, suppressMarkers: true
        });

        const request = {
            origin: shipperLatLng, destination: userLatLng, travelMode: google.maps.TravelMode.DRIVING,
        };
        directionsService.route(request, function (response, status) {
            if (status === google.maps.DirectionsStatus.OK) {
                directionsRenderer.setDirections(response);
            } else {
                alert("Không thể tìm đường: " + status);
            }
        });
    }

    setTimeout(() => {
        initMap();
        hideLoading();
    }, 1200);
});
