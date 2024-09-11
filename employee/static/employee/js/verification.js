// const form = document.querySelector('form')
// const inputs = form.querySelectorAll('input')
// const KEYBOARDS = {
//     backspace: 8,
//     arrowLeft: 37,
//     arrowRight: 39,
// }
//
// function handleInput(e) {
//     console.log('e =', e)
//     const input = e.target
//     const nextInput = input.nextElementSibling
//     if (nextInput && input.value) {
//         nextInput.focus()
//         if (nextInput.value) {
//             nextInput.select()
//         }
//     }
// }
//
// function handlePaste(e) {
//     e.preventDefault()
//     const paste = e.clipboardData.getData('text')
//     inputs.forEach((input, i) => {
//         input.value = paste[i] || ''
//     })
// }
//
// function handleBackspace(e) {
//     const input = e.target
//     if (input.value) {
//         input.value = ''
//         return
//     }
//
//     input.previousElementSibling.focus()
// }
//
// function handleArrowLeft(e) {
//     const previousInput = e.target.previousElementSibling
//     if (!previousInput) return
//     previousInput.focus()
// }
//
// function handleArrowRight(e) {
//     const nextInput = e.target.nextElementSibling
//     if (!nextInput) return
//     nextInput.focus()
// }
//
// form.addEventListener('input', handleInput)
// inputs[0].addEventListener('paste', handlePaste)
//
// inputs.forEach(input => {
//     input.addEventListener('focus', e => {
//         setTimeout(() => {
//             e.target.select()
//         }, 0)
//     })
//
//     input.addEventListener('keydown', e => {
//         switch (e.keyCode) {
//             case KEYBOARDS.backspace:
//                 handleBackspace(e)
//                 break
//             case KEYBOARDS.arrowLeft:
//                 handleArrowLeft(e)
//                 break
//             case KEYBOARDS.arrowRight:
//                 handleArrowRight(e)
//                 break
//             default:
//         }
//     })
// })
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('#verification-form');
    if (form) {
        const inputs = form.querySelectorAll('input');
        const button = form.querySelector('button');
        const KEYBOARDS = {
            backspace: 8,
            arrowLeft: 37,
            arrowRight: 39,
        }
        console.log('inputs =', inputs)

        function updateSubmitButton() {
            const allFilled = Array.from(inputs).every(input => input.value.trim() !== '');
            if (allFilled) {
                button.disabled = false;
            } else {
                button.disabled = true;
            }
        }

        function handleInput(e) {
            console.log('e =', e)
            const input = e.target
            const nextInput = input.nextElementSibling
            if (nextInput && input.value) {
                nextInput.focus()
                if (nextInput.value) {
                    nextInput.select()
                }
            }
            updateSubmitButton();
            // const allFilled = Array.from(inputs).every(input => input.value.trim() !== '');
            // if (allFilled) {
            //     console.log('All fields are filled', allFilled)
            //     form.submit();
            // }
            // else {
            //     alert('Please fill all the fields');
            // }
        }

        updateSubmitButton();

        function handlePaste(e) {
            e.preventDefault()
            const paste = e.clipboardData.getData('text')
            inputs.forEach((input, i) => {
                input.value = paste[i] || ''
            })
        }

        function handleBackspace(e) {
            const input = e.target
            if (input.value) {
                input.value = ''
                return
            }

            input.previousElementSibling.focus()
        }

        function handleArrowLeft(e) {
            const previousInput = e.target.previousElementSibling
            if (!previousInput) return
            previousInput.focus()
        }

        function handleArrowRight(e) {
            const nextInput = e.target.nextElementSibling
            if (!nextInput) return
            nextInput.focus()
        }

        console.log('form =', form)
        form.addEventListener('input', handleInput)
        console.log('form =', form)

        inputs[0].addEventListener('paste', handlePaste)

        inputs.forEach(input => {
            input.addEventListener('focus', e => {
                setTimeout(() => {
                    e.target.select()
                }, 0)
            })

            input.addEventListener('keydown', e => {
                switch (e.keyCode) {
                    case KEYBOARDS.backspace:
                        handleBackspace(e)
                        break
                    case KEYBOARDS.arrowLeft:
                        handleArrowLeft(e)
                        break
                    case KEYBOARDS.arrowRight:
                        handleArrowRight(e)
                        break
                    default:
                }
            })

        })
    } else {
        console.error('Form not found');
    }
    let totalTime = 10 * 60; // 10 minutes in seconds
    // Check if expiration timestamp is already set in local storage
    let expirationTime = localStorage.getItem('otpExpirationTime');
    window.onbeforeunload
    if (!expirationTime) {
        // Set expiration time if not already set
        expirationTime = Date.now() + totalTime * 1000;
        localStorage.setItem('otpExpirationTime', expirationTime);
    }

    function startTimer() {
        const timerElement = document.getElementById('countdown-timer');
        const interval = setInterval(() => {
            const now = Date.now();
            const timeLeft = Math.max((expirationTime - now) / 1000, 0);
            const minutes = Math.floor(timeLeft / 60);
            const seconds = Math.floor(timeLeft % 60);
            timerElement.textContent = `Code expires in ${minutes}:${seconds < 10 ? '0' + seconds : seconds} minutes `;

            if (timeLeft <= 0) {
                clearInterval(interval);
                timerElement.textContent = 'Code expired';
                localStorage.removeItem('otpExpirationTime');
            }
        }, 1000);
    }

    startTimer();

    // document.getElementById('verification-form').addEventListener('submit', function (e) {
    //     console.log('Form submitted')
    //     e.preventDefault();
    //     console.log('e.target =', e.target)
    //     const data = new FormData(e.target);
    //     fetch('/verify/', {
    //         method: 'POST',
    //         body: data
    //     })
    //         .then(response => response.json())
    //         .then(data => {
    //             if (data.success) {
    //                 localStorage.removeItem('otpExpirationTime');
    //                 window.location.href = '/dashboard/';
    //             } else {
    //                 alert('Invalid OTP');
    //             }
    //         })
    //         .catch(error => {
    //             console.error('Error:', error);
    //         });
    //
    // }, false);
    window.addEventListener('beforeunload', function (e) {
        localStorage.removeItem('otpExpirationTime');
    });
});