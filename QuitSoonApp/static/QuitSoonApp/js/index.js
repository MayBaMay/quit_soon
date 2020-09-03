$(document).ready(function () {
  // console.log("jquery loaded");
});

(function () {
  const header = document.querySelector("header");
  const content = document.querySelector(".content");
  const modalContainer = document.querySelector(".page-modals");
  const logoutModalContainer = document.querySelector(".logout-modal");

  const modalToggles = document.querySelectorAll(".toggle-modal");
  const modalContents = document.querySelectorAll(".modal-content");
  const modalActive = document.querySelector(".modal-content.content-active");
  // const closeModalBtn = document.querySelector("#close-modal");
  // const closeModalBtnLogout = document.querySelector("#close-modal-logout");
  let closeModalBtns = document.querySelectorAll(".close-modal-btn");

  const body = document.querySelector("body");

  //responsive header for tablet and lower

  function addResponsiveNav() {
    //header on scroll up
    let currentScroll = 0;
    let throttling = false;
    let throttlingT = 100;
    window.addEventListener("scroll", function () {
      if (responsive) {
        // if (!throttling) {
        //   throttling = true;
        //   setTimeout(() => {
        //     throttling = false;
        //   }, throttlingT);
        if (this.pageYOffset <= 5) {
          header.classList.remove("header-scroll");
        }
        if (this.pageYOffset > 5) {
          header.classList.add("header-scroll");
        }
        if (this.pageYOffset <= 80) {
          header.style.visibility = "visible";
          header.style.opacity = 1;
          header.style.pointerEvents = "auto";
        }
        if (this.pageYOffset > currentScroll && this.pageYOffset > 80) {
          header.style.visibility = "hidden";
          header.style.opacity = 0;
          header.style.pointerEvents = "none";
        } else {
          header.style.visibility = "visible";
          header.style.opacity = 1;
          header.style.pointerEvents = "auto";
        }
        currentScroll = this.pageYOffset;
        // }
      }
    });
  }
  let responsive;
  //on load
  if (window.innerWidth < 850) {
    responsive = true;
  } else {
    console.log("large screen");
    responsive = false;
  }
  //on resize
  window.addEventListener("resize", () => {
    if (window.innerWidth < 850) {
      responsive = true;
    } else {
      header.style.visibility = "visible";
      header.style.opacity = 1;
      header.style.pointerEvents = "auto";
      header.classList.remove("header-scroll");
      responsive = false;
    }
  });
  addResponsiveNav();

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

  if (modalActive){
    openModal(modalActive.getAttribute("id"));
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
    let p =
      document.getElementById("signIn-Password") ||
      document.getElementById("signUp-Password1");
    let icon = document.getElementById("pw-icon");
    // let hide = document.getElementById("pw-hide");
    if (p.type === "password") {
      p.type = "text";
      icon.classList = "fas fa-eye-slash";
      icon.classList = "fas fa-eye";
    } else {
      p.type = "password";
      icon.classList = "fas fa-eye";
      icon.classList = "fas fa-eye-slash";
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

  // -------- Graphs - ploty dash

  // let graphConts = document.querySelectorAll(".django-plotly-dash");
  // let iframes = Array.from(graphConts).map((c) => {
  //   return c.firstElementChild.firstElementChild;
  // });

  // let loadedFrames = 0;
  // iframes.forEach((f) =>
  //   f.addEventListener("load", () => {
  //     loadedFrames++;
  //     console.log(loadedFrames);
  //     //only add globalToggle when all graphs have loaded
  //     loadedFrames == iframes.length
  //       ? setTimeout(() => {
  //           addGlobalToggle();
  //         }, 100)
  //       : null;
  //   })
  // );

  // const inputs = {};
  // //collect all inputs and add global toggle
  // function addGlobalToggle() {
  //   iframes.forEach((f, i) => {
  //     let doc = f.contentWindow.document;
  //     let labels = doc.querySelectorAll("label");
  //     labels.forEach((label) => {
  //       inputs[label.innerText] ? null : (inputs[label.innerText] = []);
  //       inputs[label.innerText].push(label.firstElementChild);
  //       //first graph radio buttons control add graphs
  //       if (i == 0) {
  //         label.querySelector("input").addEventListener("click", (e) => {
  //           globalToggle(e);
  //         });
  //       } else {
  //         //hide other controls
  //         let controls = doc.querySelector(".graph-controls");
  //         controls.style.display = "none";
  //       }
  //     });
  //     //
  //   });
  // }

  // //first graph controls can toggles all graph inputs (providing they have the same label name e.g. "Mois")
  // function globalToggle(e) {
  //   let val, target;
  //   if (e.target.nodeName == "INPUT") {
  //     val = e.target.parentNode.innerText; //label value
  //     target = e.target;
  //   } else {
  //     val = e.target.innerText;
  //     target = e.target.firstElementChild;
  //   }
  //   inputs[val].forEach((input, i) => {
  //     if (i !== 0) {
  //       console.log("el", input);
  //       input.click();
  //     }
  //   });
  // }
})();
