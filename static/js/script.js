// Toggle the side menu visibility
function toggleMenu() {
    const menu = document.getElementById("sideMenu");
    if (menu.style.left === "0px") {
        menu.style.left = "-250px";
    } else {
        menu.style.left = "0px";
    }
}

// Optional: Close the menu when clicking outside it
document.addEventListener("click", function (event) {
    const menu = document.getElementById("sideMenu");
    const icon = document.querySelector(".menu-icon");

    if (
        menu.style.left === "0px" &&
        !menu.contains(event.target) &&
        !icon.contains(event.target)
    ) {
        menu.style.left = "-250px";
    }
});
