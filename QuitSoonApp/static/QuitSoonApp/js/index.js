$(document).ready(function () {
  console.log("jquery loaded");
});

(function () {
  // const a = 4;
  const header = document.querySelector("header");
  const content = document.querySelector(".content");
  const modalContainer = document.querySelector(".page-modals");
  const logoutModalContainer = document.querySelector(".logout-modal");

  const modalToggles = document.querySelectorAll(".toggle-modal");
  const modalContents = document.querySelectorAll(".modal-content");
  // const closeModalBtn = document.querySelector("#close-modal");
  // const closeModalBtnLogout = document.querySelector("#close-modal-logout");
  closeModalBtns = document.querySelectorAll(".close-modal-btn");

  const body = document.querySelector("body");

  //responsive header for tablet and lower

  function addResponsiveNav() {
    //header change style on scroll
    const options = {
      rootMargin: "-64px 0px 100px 0px",
      threshold: 1.0,
    };

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          header.classList.add("header-scroll");
          header.style.visibility = "hidden";
          header.style.opacity = 0;
          header.style.pointerEvents = "none";
        } else {
          header.classList.remove("header-scroll");

          //overrides scroll hiding below
          header.style.visibility = "visible";
          header.style.opacity = 1;
          header.style.pointerEvents = "auto";
        }
      });
    }, options);

    const pheading = document.querySelector(".page-heading");
    observer.observe(pheading);

    //header on scroll up
    let currentScroll = 0;
    let throttling = false;
    let throttlingT = 100;
    window.addEventListener("scroll", function () {
      if (!throttling) {
        throttling = true;
        setTimeout(() => {
          throttling = false;
        }, throttlingT);
        if (this.pageYOffset > "80") {
          // header.style.visibility = "visible";
          // header.style.opacity = 1;
          // header.style.pointerEvents = "auto";
          // return;
        }
        if (this.pageYOffset > currentScroll) {
          //down scroll
          header.style.visibility = "hidden";
          header.style.opacity = 0;
          header.style.pointerEvents = "none";
        } else {
          header.style.visibility = "visible";
          header.style.opacity = 1;
          header.style.pointerEvents = "auto";
        }
        currentScroll = this.pageYOffset;
      }
    });
  }

  //To do: won't currently add/remove resoponsive nav on resize
  if (window.innerWidth < 850) {
    addResponsiveNav();
  }

  // window.addEventListener("resize", responsiveNav);
  /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  // Modals

  function openModal(id) {
    body.style.overflowY = "hidden";

    if (id == "modal-logout") {
      body.classList.add("logout-modal-visible");
    } else {
      body.classList.add("page-modals-visible");
    }
    let modalContent = document.querySelector(`#${id}`);
    modalContent.classList.add("content-active");
  }
  function closeModal() {
    body.style.overflowY = "scroll";
    body.classList.remove("logout-modal-visible");
    body.classList.remove("page-modals-visible");

    //timeout allows transition to finish before hiding content
    setTimeout(function () {
      modalContents.forEach((m) => m.classList.remove("content-active"));
    }, 500);
  }

  // Page specific modals

  // closeModalBtn && closeModalBtn.addEventListener("click", closeModal);
  // closeModalBtnLogout.addEventListener("click", closeModal);

  closeModalBtns.forEach((btn) => btn.addEventListener("click", closeModal));

  // if (id == "modal-logout") {
  //   body.classList.add("logout-modal-visible");
  // } else {
  //   body.classList.add("page-modals-visible");
  // }
  modalToggles.forEach((toggle) =>
    toggle.addEventListener("click", () => openModal(toggle.dataset.modal))
  );

  // static modal (not real modal-  same styling but no closing/opening functionality)
  const staticM = document.querySelector(".modal-static");
  staticM && (body.style.overflowY = "hidden");

  //TO DO close modal on esc key
  //Window resize

  // //Close nav
  // window.addEventListener("resize", () => {
  //   header.classList.contains("nav-open")
  //     ? header.classList.toggle("nav-open")
  //     : null;
  // });

  //tabbed content

  const tabToggles = document.querySelectorAll(".btn-tab");

  tabToggles &&
    tabToggles.forEach((toggle) => {
      toggle.addEventListener("click", () => {
        if (toggle.classList.contains("active")) {
          return;
        }
        tabToggles.forEach((toggle) => {
          toggle.classList.remove("active");
        });
        let cont = toggle.closest(".tabbed-content-container");
        const allContent = cont.querySelectorAll(".tabbed-content");
        allContent.forEach((tc) => tc.classList.remove("active"));
        console.log(cont);
        console.log(allContent);

        let tabId = toggle.dataset.toggle;
        let tabContent = document.querySelector(`#${tabId}`);
        toggle.classList.add("active");
        tabContent.classList.add("active");
      });
    });

  //dropdown menu
  const dropdownToggles = document.querySelectorAll(".dropdown-menu");
  dropdownToggles.forEach((toggle) => {
    let menuId = toggle.dataset.toggle;
    let menu = document.querySelector(`#${menuId}`);
    let menus = document.querySelectorAll(".sub-menu");
    if ("ontouchstart" in window) {
      //click to open
      toggle.addEventListener("click", () => {
        if (menu.classList.contains("sub-menu-open")) {
          menus.forEach((menu) => menu.classList.remove("sub-menu-open"));
        } else {
          menus.forEach((menu) => menu.classList.remove("sub-menu-open"));
          menu.classList.add("sub-menu-open");
        }
      });
      //close when mouseleaves toggle or menu
    } else {
      //hover to open
      menu.addEventListener("mouseleave", () => {
        menu.classList.remove("sub-menu-open");
      });
      toggle.addEventListener("mouseleave", () => {
        menu.classList.remove("sub-menu-open");
      });
      toggle.addEventListener("mouseenter", () => {
        menu.classList.add("sub-menu-open");
      });
    }
  });

  //toggle password visibility

  //note: alternative method if using classes for toggle (e.g. fontawesome):
  // toggle classname to show different icon
  const pwtoggle = document.querySelector("#toggle-pw");
  pwtoggle && pwtoggle.addEventListener("click", (e) => togglepw(e));

  function togglepw(e) {
    e.preventDefault();
    let p = document.getElementById("password");
    let show = document.getElementById("pw-show");
    let hide = document.getElementById("pw-hide");
    if (p.type === "password") {
      p.type = "text";
      show.classList.toggle("hide");
      hide.classList.toggle("hide");
    } else {
      p.type = "password";
      show.classList.toggle("hide");
      hide.classList.toggle("hide");
    }
  }

  //outside clicks
  body.addEventListener("click", (e) => {
    //close modal when click outside
    if (e.target == modalContainer || e.target == logoutModalContainer) {
      closeModal();
    }
    //close nav dropdown menu when click outside
    let outsideClick = e.target.closest(".dropdown-menu") ? 0 : 1;
    if (outsideClick) {
      let menu = document.querySelector(".sub-menu-open");
      if (menu) {
        menu.classList.remove("sub-menu-open");
      }
    }
  });

  //TO DO close dropdown on esc key AND click anywhere else (anywhere)
})();
