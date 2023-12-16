// SIDEBAR TOGGLE

var sidebarOpen = false;
var sidebar = document.getElementById("sidebar");

function openSidebar() {
    if(!sidebarOpen) {
    sidebar.classList.add("sidebar-responsive");
    sidebarOpen = true;
    }
}

function closeSidebar() {
    if(sidebarOpen) {
    sidebar.classList.remove("sidebar-responsive");
    sidebarOpen = false;
    }
}  


const header = document.querySelector("header");

window.addEventListener("scroll", () => {
    header.classList.toggle("sticky", window.scrollY > 0);
});

const headerMenu = document.querySelector(".header__menu"),
    menuBtn = document.querySelector(".menu-btn"),
    headerMenuItems = headerMenu.querySelectorAll("li a");

menuBtn.addEventListener("click", () => {
    headerMenu.classList.toggle("show");
});

headerMenuItems.forEach((item) => {
    item.addEventListener("click" , () => {
        headerMenu.classList.remove("show");
    });
});