var myElem = document.getElementById('search');
myElem.onclick = function() {
    var room_id = $( "#rooms" ).val();
	$.post("/get_result", {room_id: room_id}, function (data) {
        if (data != null && data != undefined && data.length) {
            var html = '';
            // html += '<option value="">--Không chọn--</option>';
            html += '<div class="col-xl-12"><div class="card"><div class="card-header"></div><div class="card-block table-border-style"><div class="table-responsive"><table class="table"><thead><tr><th>Device ID</th><th>Device Name</th><th>Status</th><th>Floor</th><th>Room</th></tr></thead><tbody>';
            $.each(data, function (index, value) {
                // html += '<option value=' + value + '>' + value + '</option>';
                html += '<tr><th scope="row">' + value['device_id'] + '</th><td>' + value['device_name'] + '</td><td>'
                if (value['status'] == 1) {
                    html += '<input type="checkbox" checked class="switchbutton" value="On"/>';
                } else html += '<input type="checkbox" class="switchbutton" value="On"/>';
                html += '</td><td>' + value['floor'] + '</td><td>' + value['room_id'] + '</td></tr>';  
            });
            html += '</tbody></table></div></div></div></div>';
            $("#devices").html(html);
        }
        else $("#devices").html('');
    });
}

                                            // <tr>
                                            //     <th scope="row">1</th>
                                            //     <td>Mark</td>
                                            //     <td>Otto</td>
                                            //     <td>@mdo</td>
                                            // </tr>
                                            // <tr>
                                            //     <th scope="row">2</th>
                                            //     <td>Jacob</td>
                                            //     <td>Thornton</td>
                                            //     <td>@fat</td>
                                            // </tr>
                                            // <tr>
                                            //     <th scope="row">3</th>
                                            //     <td>Larry</td>
                                            //     <td>the Bird</td>
                                            //     <td>@twitter</td>
                                            // </tr>