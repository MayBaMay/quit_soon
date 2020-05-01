(function($) {
  "use strict"; // Start of use strict

  // Toggle the side navigation
  $("#sidebarToggle, #sidebarToggleTop").on('click', function(e) {
    $("body").toggleClass("sidebar-toggled");
    $(".sidebar").toggleClass("toggled");
    if ($(".sidebar").hasClass("toggled")) {
      $('.sidebar .collapse').collapse('hide');
    };
  });

  // Close any open menu accordions when window is resized below 768px
  $(window).resize(function() {
    if ($(window).width() < 768) {
      $('.sidebar .collapse').collapse('hide');
    };
  });

  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
  $('body.fixed-nav .sidebar').on('mousewheel DOMMouseScroll wheel', function(e) {
    if ($(window).width() > 768) {
      var e0 = e.originalEvent,
        delta = e0.wheelDelta || -e0.detail;
      this.scrollTop += (delta < 0 ? 1 : -1) * 30;
      e.preventDefault();
    }
  });

  // Scroll to top button appear
  $(document).on('scroll', function() {
    var scrollDistance = $(this).scrollTop();
    if (scrollDistance > 100) {
      $('.scroll-to-top').fadeIn();
    } else {
      $('.scroll-to-top').fadeOut();
    }
  });

  // Smooth scrolling using jQuery easing
  $(document).on('click', 'a.scroll-to-top', function(e) {
    var $anchor = $(this);
    $('html, body').stop().animate({
      scrollTop: ($($anchor.attr('href')).offset().top)
    }, 1000, 'easeInOutExpo');
    e.preventDefault();
  });

  $('#registerForm').submit(function(e){
    let formId = $(this).attr('id');
    let submitBtn = $(this).find('a[type=submit]');
    $('.username-error').css('display', 'none');
    $('.email-error').css('display', 'none');
    $('.pwd-db-error').css('display', 'none');
    $('.invalid-pwd-error').css('display', 'none');
    e.preventDefault();
    $.ajax({
      url: "/register/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
      success: function(data){
        let register_response = jQuery.parseJSON(data);
        // console.log(register_response);
        if (register_response.response == "success"){
          document.location.reload(true);
          let url = location.host;
          window.location.replace(url);
        }
        else if (register_response.response == "username already in DB") {
          $('.username-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
         else if (register_response.response == "email already in DB") {
           $('.email-error').css('display', 'block');
           submitBtn.prop('disabled', false);
        }
        else if (register_response.response == "passwords diff") {
          $('.pwd-db-error').css('display', 'block');
          console.log("diff");
          submitBtn.prop('disabled', false);
        }
        else if (register_response.response == "invalid password") {
          $('.invalid-pwd-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
      }
    })
  });

})(jQuery); // End of use strict
