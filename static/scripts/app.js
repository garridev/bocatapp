$(document).ready(function () {
  $('input[type=radio][name=creditcard]').change(function () {
    if(this.value=='new'){
      $('#creditcard-new').fadeIn('slow');
    } else {
      $('#creditcard-new').hide();
    }
  });


});
