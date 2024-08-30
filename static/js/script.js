window.onscroll = function() {
    let currentScrollPos = window.pageYOffset;
    if (prevScrollPos > currentScrollPos) {
        topBanner.style.top = "0";
        mainNav.style.top = "40px"; // Height of the top banner
    } else {
        topBanner.style.top = "-40px"; // Hide the top banner
        mainNav.style.top = "0";
    }
    prevScrollPos = currentScrollPos;
}