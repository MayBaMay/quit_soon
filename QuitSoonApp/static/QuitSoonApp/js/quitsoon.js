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

  ///////////////////show password//////////////////////

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

  ///////////////////profile page//////////////////////

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

  $('#NewEmailForm').on('submit', function(e){
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

  $('#NewPasswordForm').on('submit', function(e){
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

  var noprofile = $('#noprofile');
  if (noprofile.length ) {
    $('#modal_starting_parameters').modal('show');
  }

  $('#NewParametersForm').on('submit', function(e){
    // keep only value from form chosen
    if ($('#choose_existing_pack').hasClass('active')) {
      $('#id_type_cig').val('');
      $('#id_brand').val('');
      $('#id_qt_paquet').val('');
      $('#id_price').val('');
    }
    else if ($('#create_pack_choice').hasClass('active')){
      $('#id_ref_pack').val('');
    };
    document.location.reload(true);
  });

  newparameterspackform()

  $('.nav li').on('click', function() {
    $('.nav li').removeClass('active');
    $(this).addClass('active');
    newparameterspackform()
  });

  /////////////////paquet page////////////////////

  $('.cig-change').on('click', function(e){
    if ($(this).attr('id') == 'submit'){
      $(this).siblings(".form-cig-change").find('input[type=number]').attr('type', 'hidden');
      $(this).siblings(".form-cig-change").submit();
    }
    else {
      e.preventDefault();
      // reset all paquets rows
      $('.cig-change').prev().removeClass('hide').addClass('show');
      $('.cig-change').siblings( ".form-cig-change" ).removeClass('show').addClass('hide');
      $('.cig-change').removeAttr('id','submit')
      // change only this row
      $(this).prev().removeClass('show').addClass('hide');
      $(this).siblings(".form-cig-change").removeClass('hide').addClass('show');
      $(this).attr('id', 'submit')
      // $(this).removeClass('cig-change').addclass('id','cig-change')
    }
  });

  /////////////////alternative page////////////////////

  $('#id_substitut').prop('required',false);
  $('#id_nicotine').prop('required',false);
  $('#id_type_activity').prop('required',true);
  $('#id_activity').prop('required',true);
  $('.activity_form').removeClass('hide').addClass('show');
  $('.substitut_form').removeClass('show').addClass('hide');

  $('#id_type_alternative').on('change', function(e) {

    // IF VALUE TYPE == SUBSTITUT   --->   SHOW SUBSTITUT FORM
   if ($(this).val() == 'Su') {
     $('#id_type_activity').prop('required',false).val('');
     $('#id_activity').prop('required',false).val('');
     $('#id_substitut').prop('required',true);
     $('#id_nicotine').prop('required',true);
     $('.activity_form').removeClass('show').addClass('hide');
     $('.substitut_form').removeClass('hide').addClass('show');
    }
   // ELSE   --->    SHOW ACTIVITY FORM
   else {
     $('#id_substitut').prop('required',false).val('');
     $('#id_nicotine').prop('required',false).val('');
     $('#id_type_activity').prop('required',true);
     $('#id_activity').prop('required',true);
     $('.activity_form').removeClass('hide').addClass('show');
     $('.substitut_form').removeClass('show').addClass('hide');
   }
  });

  /////////////////smoke page////////////////////

  displayPaquetsFields();

  $('#id_given_field').change(function() {
      if (this.checked) {
          $('.show').removeClass('show').addClass('hide');
          $('.showtypes').removeClass('showtypes').addClass('hidetypes');
      } else {
          $('.hidetypes').removeClass('hidetypes').addClass('showtypes');
          displayPaquetsFields();
      }
  });

  $('#id_type_cig_field').on('change', function(e) {
    $('.show').removeClass('show').addClass('hide');
    displayPaquetsFields()
  });

  /////////////////healthy activity page////////////////////

  displayAlternativeFields()
  $('#id_type_alternative_field').on('change', function(e) {
    $('.show').removeClass('show').addClass('hide');
    $('#id_duration_hour').removeClass('hide').addClass('show');
    $('#id_duration_min').removeClass('hide').addClass('show');
    displayAlternativeFields()
  });

  $('#id_su_field').on('change', function(e) {
    displayAlternativeFields()
  });

})(jQuery); // End of use strict

var dateField = document.querySelector('.currentDate');
var timeField = document.querySelector('.currentTime');
var date = new Date();

// Set the date & time
if (dateField) {
  dateField.value = date.getFullYear().toString() + '-' +
    (date.getMonth() + 1).toString().padStart(2, 0) +
    '-' + date.getDate().toString().padStart(2, 0);
}
if (timeField) {
  timeField.value = date.getHours().toString().padStart(2, 0) + ':' +
    date.getMinutes().toString().padStart(2, 0);
}

function displayPaquetsFields(){
  if ($('#id_type_cig_field').val() == 'IND') {
    $('#id_indus_pack_field').removeClass('hide').addClass('show');
  }
  else if ($('#id_type_cig_field').val() == 'ROL') {
    $('#id_rol_pack_field').removeClass('hide').addClass('show');
  }
  else if ($('#id_type_cig_field').val() == 'CIGARES') {
    $('#id_cigares_pack_field').removeClass('hide').addClass('show');
  }
  else if ($('#id_type_cig_field').val() == 'PIPE') {
      $('#id_pipe_pack_field').removeClass('hide').addClass('show');
  }
  else if ($('#id_type_cig_field').val() == 'NB') {
    $('#id_nb_pack_field').removeClass('hide').addClass('show');
  }
  else if ($('#id_type_cig_field').val() == 'GR') {
    $('#id_gr_pack_field').removeClass('hide').addClass('show');
  };
};

function displayAlternativeFields(){
  var su = {
    'type_alternative_field':$('#id_type_alternative_field').serialize(),
    'su_field':$('#id_su_field').serialize(),
  }
  $.ajax({
    url: "/su_ecig/", // the file to call
    type: "GET", // GET or POST
    data: su, // get the form data
    })
    .done(function(data) {
      var ecig = jQuery.parseJSON(data);
      if (ecig.response == 'true') {
          $('#id_ecig_vape_or_start').removeClass('hide').addClass('show');
          $('#id_ecig_vape_or_start_0').removeClass('hide').addClass('show');
          $('#id_ecig_vape_or_start_1').removeClass('hide').addClass('show');
      }
      else {
        $('#id_ecig_vape_or_start').removeClass('show').addClass('hide');
        $('#id_ecig_vape_or_start_0').removeClass('show').addClass('hide');
        $('#id_ecig_vape_or_start_1').removeClass('show').addClass('hide');
      }
    });
  if ($('#id_type_alternative_field').val() == 'Sp') {
    $('#id_sp_field').removeClass('hide').addClass('show');
  }
  else if ($('#id_type_alternative_field').val() == 'So') {
    $('#id_so_field').removeClass('hide').addClass('show');
  }
  else if ($('#id_type_alternative_field').val() == 'Lo') {
    $('#id_lo_field').removeClass('hide').addClass('show');
  }
  else if ($('#id_type_alternative_field').val() == 'Su') {
    $('#id_su_field').removeClass('hide').addClass('show');
    $('#id_duration_hour').removeClass('show').addClass('hide');
    $('#id_duration_min').removeClass('show').addClass('hide');
  }
};

function newparameterspackform(){
  if ($('#choose_existing_pack').hasClass('active')) {
    console.log('choose_existing_pack');
    $('#existing_packs').removeClass('hide').addClass('show');
    $('.newpackform').removeClass('show').addClass('hide');
    $('#id_ref_pack').prop('required',true);
    $('#id_type_cig').prop('required',false);
    $('#id_brand').prop('required',false);
    $('#id_qt_paquet').prop('required',false);
    $('#id_price').prop('required',false);
  };
  if ($('#create_pack_choice').hasClass('active')){
    console.log('create_pack_choice');
    $('.newpackform').removeClass('hide').addClass('show');
    $('#existing_packs').removeClass('show').addClass('hide');
    $('#id_ref_pack').prop('required',false);
    $('#id_type_cig').prop('required',true);
    $('#id_brand').prop('required',true);
    $('#id_qt_paquet').prop('required',true);
    $('#id_price').prop('required',true);
  };
}
