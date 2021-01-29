$(document).ready(function() {
    $(document).on("click","input[type='checkbox']", function() {
     // var element = document.getElementById("but");
     // while(element){
     //   if(element.clicked == true){
     //     var current_status = element.checked;
     //     break;
     //   }
     //   else{
     //     element = document.getElementById("but");
     //   }
     // } 
     //var current_status = $(this).is(':checked');
    //  var room = document.getElementById("rooms").innerHTML;
     var b = this.parentNode.parentNode.cells[0].textContent;
    //  console.log(this.value);
     var current_status;
     console.log(this.checked);
     if (this.checked === true) current_status = 'On';
     else current_status = 'Off';  
     if(current_status == 'On' || current_status == 'Off'){
     $.ajax({
      url: "/get_toggled_status",
      type: "get",
       data: {device_id: b, status: current_status},
       success: function(response) {
        $(".status").html(response);
       },
       error: function(xhr) {
         document.write('error');
       }
     });}
     else{
       alert('Your press failed, please reset and press again');
     }
    });
  });