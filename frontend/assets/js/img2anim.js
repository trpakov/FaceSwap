function preview() {
    var parent = document.getElementById('col_1');
    var frame_source = document.getElementById("frame_source");

    if (frame_source != null) {
        parent.removeChild(frame_source);
    }

    var frame_source = document.createElement("img");
    frame_source.id = "frame_source";
    frame_source.className = "img-fluid mx-auto d-block";
    frame_source.setAttribute("data-aos", "fade-bottom");
    frame_source.setAttribute("data-aos-delay", "100");
    frame_source.style.marginTop = "5%";
    frame_source.style.marginBottom = "5%";
    frame_source.src = URL.createObjectURL(document.getElementById("formFile_src").files[0]);
    parent.append(frame_source);

}

function send() {

    $('html,body').animate({ scrollTop: $("#showtime").offset().top }, 'slow');

    var photo_src = document.getElementById("formFile_src").files[0];
    var photo_dest_url = document.getElementById("frame_dest").src;

    if(photo_src === undefined){
        $('#modal-title').text('Not so fast!');
        $('#modal-text').text('Please, choose source image.');
        $('#myModal').modal('show');
        return;
    }

    var  data = new FormData();

    data.append("source", photo_src);
    // data.append("dest_url", photo_dest_url);
    // fetch('/swap', {method: "POST", body: data});

    $(document).ajaxStart(function () {
        $('#loader').show();
        $('#result_img').attr('style', 'display:none !important');
    });

    $(document).ajaxStop(function () {
        $('#loader').hide();
    });

    $.ajax({
        type: 'POST',
        url: '/swap_gif/' + photo_dest_url,
        cache: false,
        contentType: false,
        processData: false,
        data: data,
        success: function (result) {
            console.log(result);
            var parent = document.getElementById('result_container');
            var result_img = document.getElementById("result_img");

            if (result_img != null) {
                parent.removeChild(result_img);
            }

            var result_img = document.createElement('img');
            result_img.id = "result_img";
            result_img.className = "img-fluid mx-auto d-block rounded";
            result_img.setAttribute("data-aos", "fade-bottom");
            result_img.style.marginTop = "5%";
            result_img.style.marginBottom = "5%";
            result_img.style.width = "auto";
            result_img.style.height = "500px";
            result_img.style.float = "none";
            result_img.src = result
            parent.append(result_img)

        },
        error: function (err) {

            $('#modal-title').text('Something Went Wrong :(')
            $("#modal-text").text(err.responseJSON['detail'])
            $('#myModal').modal('show');
        }
    })
}

document.addEventListener('DOMContentLoaded', function () {

    if (document.getElementById("formFile_src").files.length != 0) {
        preview('source');
    }

});

function img_click(event) {
    
    $("#show-more").hide(500)
    $('.gif-image').each(function () {
        $(this).hide(500);
    })
    var  parent = document.getElementById('dest_div');
    var div = document.createElement("div");
    div.setAttribute('class', 'row');
    var dest = document.createElement("img");
    dest.id = "frame_dest";
    dest.className = "img-fluid mx-auto";
    // dest.setAttribute("data-aos", "fade-bottom");
    // dest.setAttribute("data-aos-delay", "100");
    dest.style.width = "auto";
    dest.style.height = "500px";
    dest.style.marginTop = "5%";
    dest.style.marginBottom = "5%";
    dest.src = event.target.src;
    // $('.cls').attr('style','display:none');
    $(dest).hide()

    dest.onclick = function () {
        $(this).hide(500, function () { $(this).remove(); });
        $('#showtime').hide(500, function () { $(this).remove(); });
        $('.gif-image').each(function () { $(this).show(500); });
        $("#show-more").show(500)
    }

    // <button onclick="send()" id="showtime" class="btn btn-primary mt-3">Showtime!</button>

    var btn = document.createElement('button');
    btn.setAttribute('onclick', 'send()');
    btn.setAttribute('class', 'btn btn-primary mt-3');
    btn.setAttribute('id', 'showtime');
    btn.textContent = 'Showtime!';
    $(btn).hide()

    div.append(dest);
    div.append(btn);
    parent.append(div);
    $(dest).show(500)
    $(btn).show(500)
}

