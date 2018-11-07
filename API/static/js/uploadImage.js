function previewFile() {
    var preview = document.querySelector('img');
    var file = document.querySelector('input[type=file]').files[0];
    var reader = new FileReader();
    var imageDataInput = document.getElementById('imageBase64');

    reader.addEventListener("load", function () {
        preview.src = reader.result;
        imageDataInput.value = preview.src;
    }, false);

    // reader.onloadend = function () {
    //     preview.src = reader.result;
    //     imageDataInput.value = reader.result;
    // }

    if (file) {
        reader.readAsDataURL(file);


    } else {
        preview.src = "";
    }
}