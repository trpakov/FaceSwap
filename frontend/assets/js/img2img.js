function preview(type) {

    if (type === 'source') {

        var parent = document.getElementById('col_1');
        var frame_source = document.getElementById("frame_source");

        if (frame_source != null) {
            parent.removeChild(frame_source);
        }

        var frame_source = document.createElement("img");
        frame_source.id = "frame_source";
        frame_source.className = "img-fluid center-block";
        frame_source.setAttribute("data-aos", "fade-right");
        frame_source.style.marginTop = "5%";
        frame_source.style.marginBottom = "5%";
        frame_source.src = URL.createObjectURL(document.getElementById("formFile_src").files[0]);
        parent.append(frame_source);

    } else {

        var parent = document.getElementById('col_2');
        var frame_dest = document.getElementById("frame_dest");

        if (frame_dest != null) {
            parent.removeChild(frame_dest);
        }

        var frame_dest = document.createElement("img");
        frame_dest.id = "frame_dest";
        frame_dest.className = "img-fluid center-block";
        frame_dest.setAttribute("data-aos", "fade-left");
        frame_dest.style.marginTop = "5%";
        frame_dest.style.marginBottom = "5%";
        frame_dest.src = URL.createObjectURL(document.getElementById("formFile_dest").files[0]);
        parent.append(frame_dest);

    }
}

function send() {

    $('html,body').animate({ scrollTop: $("#showtime").offset().top }, 'slow');

    var photo_src = document.getElementById("formFile_src").files[0];
    var photo_dest = document.getElementById("formFile_dest").files[0];

    if(photo_src === undefined || photo_dest === undefined){
        $('#modal-title').text('Not so fast!');
        $('#modal-text').text('Please, choose source and destination image.');
        $('#myModal').modal('show');
        return;
    }

    var data = new FormData();

    data.append("source", photo_src);
    data.append("dest", photo_dest);
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
        url: '/swap',
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
            result_img.style.float = "none";
            result_img.src = result
            parent.append(result_img)

        },
        error: function (err) {
            // console.log(err);
            $('#modal-title').text('Oh no :(');
            $("#modal-text").text(err.responseJSON['detail']);
            $('#myModal').modal('show');
        }
    })
}

document.addEventListener('DOMContentLoaded', function () {

    if (document.getElementById("formFile_src").files.length != 0) {
        preview('source');
    }
    if (document.getElementById("formFile_dest").files.length != 0) {
        preview('dest');
    }

});


switcher = document.getElementById('view-switch')
switcher.onclick = function () {
    $('#img-upload').toggle(500);
    $('#img-url').toggle(500, function() {
        if ($(this).css('display') != 'none') {
            testImages(click=false);
        }
    })
}

async function testImages(click) {
    photo_src_url = document.getElementById("source-url").value;
    photo_dest_url = document.getElementById("dest-url").value;

    src_valid = undefined;
    dest_valid = undefined;

    $('#frame_source_url').hide()
    $('#loader_src').show();

    const srcTask = testImage(photo_src_url).then(
        function () { 
            src_valid = true;
            previewUrl('source');
     }, function () { 
            src_valid = false;
            $('#frame_source_url').hide(500, function() {$(this).remove()});
         });

    $('#frame_dest_url').hide()
    $('#loader_dest').show();

    const destTask = testImage(photo_dest_url).then(
        function () { 
            dest_valid = true; 
            previewUrl('dest');
        }, function () { 
            dest_valid = false; 
            $('#frame_dest_url').hide(500, function() {$(this).remove()});      
        });

    await srcTask
    await destTask
    
    $('#loader_src').hide();
    $('#loader_dest').hide();

    if(click){
        sendUrl(src_valid, dest_valid);
    }
}

function testImage(url) {
    return new Promise(function (resolve, reject) {
        var timeout = 1500;
        var timer, img = new Image();
        img.onerror = img.onabort = function () {
            clearTimeout(timer);
            reject("error");
        };
        img.onload = function () {
            clearTimeout(timer);
            resolve("success");
        };
        timer = setTimeout(function () {
            // reset .src to invalid URL so it stops previous
            // loading, but doens't trigger new load
            img.src = "//!!!!/noexist.jpg";
            reject("timeout");
        }, timeout);
        img.src = url;
    });
}


function sendUrl(valid_src, valid_dest) {

    valid = valid_src && valid_dest

    if (!valid) {
        $('#modal-title').text('Something Went Wrong :(')
        $("#modal-text").text("Make sure that you entered valid image URLs and try again.")
        $('#myModal').modal('show');
        return;
    }

    $(document).ajaxStart(function () {
        $('#loader').show();
        $('#result_img').attr('style', 'display:none !important');
    });

    $(document).ajaxStop(function () {
        $('#loader').hide();
    });

    $.ajax({
        type: 'GET',
        url: '/swap_urls',
        cache: false,
        contentType: false,
        processData: false,
        data: $.param({ 'source_url': photo_src_url, 'dest_url': photo_dest_url }),
        success: function (result) {
            console.log(result);
            parent = document.getElementById('result_container');
            result_img = document.getElementById("result_img");

            if (result_img != null) {
                parent.removeChild(result_img);
            }

            result_img = document.createElement('img');
            result_img.id = "result_img";
            result_img.className = "img-fluid mx-auto d-block rounded";
            result_img.setAttribute("data-aos", "fade-bottom");
            result_img.style.marginTop = "5%";
            result_img.style.marginBottom = "5%";
            result_img.style.float = "none";
            result_img.src = result
            parent.append(result_img)

        },
        error: function (err) {
            
            $('#modal-title').text('Oh no :(');
            $("#modal-text").text(err.responseJSON['detail']);
            $('#myModal').modal('show');
        }
    })
}



function previewUrl(type) {

    if (type === 'source') {

        parent = document.getElementById('col_1_url');
        frame_source = document.getElementById("frame_source_url");

        if (frame_source != null) {
            parent.removeChild(frame_source);
        }

        frame_source = document.createElement("img");
        frame_source.id = "frame_source_url";
        frame_source.className = "img-fluid center-block";
        frame_source.setAttribute("data-aos", "fade-right");
        frame_source.style.marginTop = "5%";
        frame_source.style.marginBottom = "5%";
        frame_source.src = document.getElementById("source-url").value;
        parent.append(frame_source);

    } else {

        parent = document.getElementById('col_2_url');
        frame_dest = document.getElementById("frame_dest_url");

        if (frame_dest != null) {
            parent.removeChild(frame_dest);
        }

        frame_dest = document.createElement("img");
        frame_dest.id = "frame_dest_url";
        frame_dest.className = "img-fluid center-block";
        frame_dest.setAttribute("data-aos", "fade-left");
        frame_dest.style.marginTop = "5%";
        frame_dest.style.marginBottom = "5%";
        frame_dest.src = document.getElementById("dest-url").value;
        parent.append(frame_dest);
    }
}
