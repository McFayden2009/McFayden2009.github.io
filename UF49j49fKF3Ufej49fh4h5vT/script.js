document.addEventListener('DOMContentLoaded', function() {
            setTimeout(function() {
                // Add the 'hidden' class to start the fade-out effect
                document.getElementById('loader').classList.add('hidden');

                // Optionally, hide the element completely after the fade-out effect
                setTimeout(function() {
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('login-box').style.display = 'block';
                    document.getElementById('login-box-form').style.display = 'inline-block';
                }, 1000); // 1000 milliseconds = 1 second
            }, 5000); // 5000 milliseconds = 5 seconds
        });
