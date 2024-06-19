document.addEventListener('DOMContentLoaded', function () {
    var modal = document.getElementById("order-modal");
    var closeBtn = document.getElementsByClassName("close")[0];
    var closeFooterBtn = document.getElementsByClassName("close-btn")[0];
    var orderDetailsLinks = document.getElementsByClassName("order-details");

    Array.from(orderDetailsLinks).forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            modal.style.display = "block";
        });
    });

    closeBtn.onclick = function () {
        modal.style.display = "none";
    }

    closeFooterBtn.onclick = function () {
        modal.style.display = "none";
    }

    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});
