(function ($) {
  "use strict"; // Start of use strict

  // function get_time_zone_offset( ) {
  // var current_date = new Date();
  // return parseInt(-current_date.getTimezoneOffset() / 60);
  // }
  // console.log(get_time_zone_offset());




  ///////////////////show password//////////////////////

  $(".pass-status").on("click", function (e) {
    var passwordInput = $(".password-field");
    var passStatus = $(".pass-status");

    if (passwordInput.prop("type") == "password") {
      passwordInput.prop("type", "text");
      passStatus.toggleClass("fa-eye fa-eye-slash");
    } else {
      passwordInput.prop("type", "password");
      passStatus.toggleClass("fa-eye-slash fa-eye");
    }
  });

  $(".form-with-password").on("submit", function (e) {
    var passwordInput = $(".password-field");
    passwordInput.prop("type", "password");
    return true;
  });

  ///////////////////profile page//////////////////////

  $("#NewNameForm").on("submit", function (e) {
    var form = $(this);
    var submitBtn = $(this).find("input[type=submit]");
    $(".username-error").css("display", "none");
    $(".newname-error").css("display", "none");
    e.preventDefault();
    $.ajax({
      url: "/new_name/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
    }).done(function (data) {
      var new_name_response = jQuery.parseJSON(data);
      if (new_name_response.response == "success") {
        document.location.reload(true);
        // $("#modal_change_username").modal("hide");
      } else if (new_name_response.response == "name already in db") {
        $(".username-error").css("display", "block");
        submitBtn.prop("disabled", false);
      } else {
        $(".newname-error").css("display", "block");
        submitBtn.prop("disabled", false);
      }
    });
  });

  $("#NewEmailForm").on("submit", function (e) {
    var form = $(this);
    var submitBtn = $(this).find("input[type=submit]");
    $(".newemail-error").css("display", "none");
    $(".dbemail-error").css("display", "none");
    e.preventDefault();
    $.ajax({
      url: "/new_email/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
    }).done(function (data) {
      var new_email_response = jQuery.parseJSON(data);
      if (new_email_response.response == "success") {
        document.location.reload(true);
        // $("#modal_change_email").modal("hide");
      } else if (new_email_response.response == "email already in DB") {
        $(".dbemail-error").css("display", "block");
        submitBtn.prop("disabled", false);
      } else {
        $(".newemail-error").css("display", "block");
        submitBtn.prop("disabled", false);
      }
    });
  });

  $("#NewPasswordForm").on("submit", function (e) {
    var form = $(this);
    var submitBtn = $(this).find("input[type=submit]");
    $(".oldpwd-error").css("display", "none");
    $(".newpwd-error").css("display", "none");
    $(".dbpwd-error").css("display", "none");
    $(".newpassword-error").css("display", "none");
    e.preventDefault();
    $.ajax({
      url: "/new_password/", // the file to call
      type: "POST", // GET or POST
      data: $(this).serialize(), // get the form data
    }).done(function (data) {
      var new_password_response = jQuery.parseJSON(data);
      if (new_password_response.response == "success") {
        document.location.reload(true);
        // $("#modal_change_password").modal("hide");
      } else if (new_password_response.response == "incorrect old password") {
        $(".oldpwd-error").css("display", "block");
        submitBtn.prop("disabled", false);
      } else if (
        new_password_response.response == "new password not confirmed"
      ) {
        $(".dbpwd-error").css("display", "block");
        submitBtn.prop("disabled", false);
      } else if (new_password_response.response == "incorrect newpassword") {
        $(".newpwd-error").css("display", "block");
        submitBtn.prop("disabled", false);
      } else {
        $(".newpassword-error").css("display", "block");
        submitBtn.prop("disabled", false);
      }
    });
  });

  var noprofile = $("#noprofile");
  if (noprofile.length) {
    // $("#modal_starting_parameters").modal("show");
  }

  $("#NewParametersForm").on("submit", function () {
    // keep only value from form chosen
    if ($("#choose_existing_pack").hasClass("active")) {
      $("#id_type_cig").val("");
      $("#id_brand").val("");
      $("#id_qt_paquet").val("");
      $("#id_price").val("");
    } else if ($("#create_pack_choice").hasClass("active")) {
      $("#id_ref_pack").val("");
    }
    document.location.reload(true);
  });

  newparameterspackform();

  $(".param-tab").on("click", function () {
    newparameterspackform();
  });

  /////////////////paquet page////////////////////

  // properties could have been change in profile page while saving ref_pack
  $(".fa-smoking").on("click", function () {
    $("#id_type_cig")
      .prop("required", true)
      .removeClass("hide")
      .addClass("show");
  });

  // modify g/cig form
  $(".cig-change").on("click", function (e) {
    if ($(this).attr("id") == "submit") {
      $(this)
        .siblings(".form-cig-change")
        .find("input[type=number]")
        .attr("type", "hidden");
      $(this).siblings(".form-cig-change").submit();
    } else {
      e.preventDefault();
      // reset all paquets rows
      $(".cig-change").prev().removeClass("hide").addClass("show");
      $(".cig-change")
        .siblings(".form-cig-change")
        .removeClass("show")
        .addClass("hide");
      $(".cig-change").removeAttr("id", "submit");
      // change only this row
      $(this).prev().removeClass("show").addClass("hide");
      $(this).siblings(".form-cig-change").removeClass("hide").addClass("show");
      $(this).attr("id", "submit");
      // $(this).removeClass('cig-change').addclass('id','cig-change')
    }
  });

  /////////////////alternative page////////////////////

  $("#alternativeform select[id=id_substitut]").prop("required", false);
  $("#alternativeform input[id=id_nicotine]").prop("required", false);
  $("#alternativeform select[id=id_type_activity]").prop("required", true);
  $("#alternativeform input[id=id_activity]").prop("required", true);
  $(".activity_form").removeClass("hide").addClass("show");
  $(".substitut_form").removeClass("show").addClass("hide");

  $("#alternativeform select[id=id_type_alternative]").on("change", function (
    e
  ) {
    // IF VALUE TYPE == SUBSTITUT   --->   SHOW SUBSTITUT FORM
    if ($(this).val() == "Su") {
      $(".activity_form").removeClass("show").addClass("hide");
      $(".substitut_form").removeClass("hide").addClass("show");
      $("#alternativeform select[id=id_type_activity]")
        .prop("required", false)
        .val("");
      $("#alternativeform input[id=id_activity]")
        .prop("required", false)
        .val("");
      $("#alternativeform select[id=id_substitut]").prop("required", true);
      $("#alternativeform input[id=id_nicotine]").prop("required", true);
    }
    // ELSE   --->    SHOW ACTIVITY FORM
    else {
      $(".activity_form").removeClass("hide").addClass("show");
      $(".substitut_form").removeClass("show").addClass("hide");
      $("#alternativeform select[id=id_substitut]")
        .prop("required", false)
        .val("");
      $("#alternativeform input[id=id_nicotine]")
        .prop("required", false)
        .val("");
      $("#alternativeform select[id=id_type_activity]").prop("required", true);
      $("#alternativeform input[id=id_activity]").prop("required", true);
    }
  });

  /////////////////smoke page////////////////////

  displayPaquetsFields();

  $("#id_given_field").change(function () {
    if (this.checked) {
      $("#cig_details").removeClass("show").addClass("hide");
    } else {
      $("#cig_details").removeClass("hide").addClass("show");
      displayPaquetsFields();
    };
  });

  $("#id_type_cig_field").on("change", function (e) {
    if ($("#cig_details").hasClass("show")) {
      $(".show").removeClass("show").addClass("hide");
      displayPaquetsFields();
    };
  });

  /////////////////healthy activity page////////////////////
  if (window.location.pathname === "/health/") {
    displayAlternativeFields();
    $("#id_type_alternative_field").on("change", function (e) {
      $(".show").removeClass("show").addClass("hide");
      $("#duration-group").removeClass("hide").addClass("show-flex");
      $("#id_duration_hour").removeClass("hide").addClass("show");
      $("#id_duration_min").removeClass("hide").addClass("show");
      displayAlternativeFields();
    });
    $("#healthform select[id=id_su_field]").on("change", function (e) {
      displayAlternativeFields();
    });
  }
})(jQuery); // End of use strict

var dateField = document.querySelector(".currentDate");
var timeField = document.querySelector(".currentTime");
var date = new Date();

// Set the date & time
if (dateField) {
  dateField.value =
    date.getFullYear().toString() +
    "-" +
    (date.getMonth() + 1).toString().padStart(2, 0) +
    "-" +
    date.getDate().toString().padStart(2, 0);
};
if (timeField) {
  timeField.value =
    date.getHours().toString().padStart(2, 0) +
    ":" +
    date.getMinutes().toString().padStart(2, 0);
};

function displayPaquetsFields() {
  if ($("#cig_details").hasClass("show")) {
    if ($("#id_type_cig_field").val() == "IND") {
      $("#id_ind_pack_field").removeClass("hide").addClass("show");
    } else if ($("#id_type_cig_field").val() == "ROL") {
      $("#id_rol_pack_field").removeClass("hide").addClass("show");
    }
  }
};

function displayAlternativeFields() {
  var su = {
    type_alternative_field: $(
      "#healthform select[name=type_alternative_field]"
    ).serialize(),
    su_field: $("#healthform select[name=su_field]").serialize(),
  };
  $.ajax({
    url: "/su_ecig/", // the file to call
    type: "GET", // GET or POST
    data: su, // get the form data
  }).done(function (data) {
    var ecig = jQuery.parseJSON(data);
    if (ecig.response == "true") {
      $("#id_ecig_vape_or_start").removeClass("hide").addClass("show");
      $("#id_ecig_vape_or_start_0").removeClass("hide").addClass("show");
      $("#id_ecig_vape_or_start_1").removeClass("hide").addClass("show");
    } else {
      $("#id_ecig_vape_or_start").removeClass("show").addClass("hide");
      $("#id_ecig_vape_or_start_0").removeClass("show").addClass("hide");
      $("#id_ecig_vape_or_start_1").removeClass("show").addClass("hide");
    }
  });

  if ($("#id_type_alternative_field").val() == "Sp") {
    $("#id_sp_field").removeClass("hide").addClass("show");
  } else if ($("#id_type_alternative_field").val() == "So") {
    $("#id_so_field").removeClass("hide").addClass("show");
  } else if ($("#id_type_alternative_field").val() == "Lo") {
    $("#id_lo_field").removeClass("hide").addClass("show");
  } else if ($("#id_type_alternative_field").val() == "Su") {
    $("#id_su_field").removeClass("hide").addClass("show");
    $("#duration-group").removeClass("show-flex").addClass("hide");
    $("#id_duration_hour").removeClass("show").addClass("hide");
    $("#id_duration_min").removeClass("show").addClass("hide");
  }
};

function newparameterspackform() {
  if ($("#choose_existing_pack").hasClass("active")) {
    $("#id_ref_pack").prop("required", true);
    $("#id_type_cig").prop("required", false);
    $("#id_brand").prop("required", false);
    $("#id_qt_paquet").prop("required", false);
    $("#id_price").prop("required", false);
  };
  if ($("#create_pack_choice").hasClass("active")) {
    $("#id_ref_pack").prop("required", false);
    $("#id_type_cig").prop("required", true);
    $("#id_brand").prop("required", true);
    $("#id_qt_paquet").prop("required", true);
    $("#id_price").prop("required", true);
  }
};
