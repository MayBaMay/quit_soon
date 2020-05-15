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

  $('.pass-status').on('click', function(e){
    var passwordInput = $('.password-field');
    var passStatus = $('.pass-status');

    if (passwordInput.prop('type') == 'password'){
      passwordInput.prop('type','text');
      passStatus.toggleClass('fa-eye fa-eye-slash');
    }
    else{
      passwordInput.prop('type','password');
      passStatus.toggleClass('fa-eye-slash fa-eye');
    }
  });

  $('.form-with-password').on('submit', function(e){
    var passwordInput = $('.password-field');
    passwordInput.prop('type','password');
    return true;
  });

  $('#NewNameForm').on('submit', function(e){
    var form = $(this);
    var submitBtn = $(this).find('input[type=submit]');
    $('.username-error').css('display', 'none');
    $('.newname-error').css('display', 'none');
    e.preventDefault();
    $.ajax({
      url: "/new_name/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
      })
      .done(function(data) {
        var new_name_response = jQuery.parseJSON(data);
        if (new_name_response.response == "success"){
          document.location.reload(true);
          $('#modal_change_username').modal('hide');
        }
        else if (new_name_response.response == "name already in db"){
          $('.username-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
        else {
          $('.newname-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
      });
  });

  $('#NewEmailForm').submit(function(e){
    var form = $(this);
    var submitBtn = $(this).find('input[type=submit]');
    $('.newemail-error').css('display', 'none');
    $('.dbemail-error').css('display', 'none');
    e.preventDefault();
    $.ajax({
      url: "/new_email/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
      })
      .done(function(data) {
        var new_email_response = jQuery.parseJSON(data);
        if (new_email_response.response == "success"){
          document.location.reload(true);
          $('#modal_change_email').modal('hide');
        }
        else if (new_email_response.response == "email already in DB"){
          $('.dbemail-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
        else {
          $('.newemail-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
      });
  });

  $('#NewPasswordForm').submit(function(e){
    var form = $(this);
    var submitBtn = $(this).find('input[type=submit]');
    $('.oldpwd-error').css('display', 'none');
    $('.newpwd-error').css('display', 'none');
    $('.dbpwd-error').css('display', 'none');
    $('.newpassword-error').css('display', 'none');
    e.preventDefault();
    $.ajax({
      url: "/new_password/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
      })
      .done(function(data) {
        var new_password_response = jQuery.parseJSON(data);
        if (new_password_response.response == "success"){
          document.location.reload(true);
          $('#modal_change_password').modal('hide');
        }
        else if (new_password_response.response == "incorrect old password"){
          $('.oldpwd-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
        else if (new_password_response.response == "new password not confirmed"){
          $('.dbpwd-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
        else if (new_password_response.response == "incorrect newpassword"){
          $('.newpwd-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
        else {
          $('.newpassword-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
      });
  });

  $('#NewParametersForm').submit(function(e){
    var form = $(this);
    var submitBtn = $(this).find('input[type=submit]');
    $('.newparameters-error').css('display', 'none');
    e.preventDefault();
    $.ajax({
      url: "/new_parameters/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
      })
      .done(function(data) {
        var new_parameters_response = jQuery.parseJSON(data);
        if (new_parameters_response.response == "success"){
          document.location.reload(true);
          $('#modal_starting_parameters').modal('hide');
        }
        else {
          $('.newparameters-error').css('display', 'block');
          submitBtn.prop('disabled', false);
        }
      });
  });


})(jQuery); // End of use strict
