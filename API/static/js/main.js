$(document).ready(function () {
  var videoSelect = document.querySelector("select#videoSource");
  var selectors = [videoSelect];
  const video = document.getElementById('preview');
  const canvas = document.getElementById('canvas');

  var button = document.getElementById('submit_picture_button');
  button.onclick = function () {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    var context = canvas.getContext('2d');
    context.drawImage(video, 0, 0)
    var imageData = atob(canvas.toDataURL('type/png'))
    var form = document.getElementById('myForm');
    var formData = new FormData();
    formData.append("imageData", imageData);
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/detect");
    xmlhttp.send(formData);
  }



  function gotDevices(deviceInfos) {
    // Handles being called several times to update labels. Preserve values.
    var values = selectors.map(function (select) {
      return select.value;
    });
    selectors.forEach(function (select) {
      while (select.firstChild) {
        select.removeChild(select.firstChild);
      }
    });

    for (var i = 0; i !== deviceInfos.length; ++i) {
      var deviceInfo = deviceInfos[i];
      var option = document.createElement("option");
      option.value = deviceInfo.deviceId;

      if (deviceInfo.kind === "videoinput") {
        option.text = deviceInfo.label || "camera " + (videoSelect.length + 1);
        videoSelect.appendChild(option);
      } else {
        console.log("Some other kind of source/device: ", deviceInfo);
      }

      selectors.forEach(function (select, selectorIndex) {
        if (
          Array.prototype.slice.call(select.childNodes).some(function (n) {
            return n.value === values[selectorIndex];
          })
        ) {
          select.value = values[selectorIndex];
        }
      });
    }
  }

  navigator.mediaDevices
    .enumerateDevices()
    .then(gotDevices)
    .catch(handleError);

  function gotStream(stream) {
    // arToolkitSource.domElement.srcObject = stream; // make stream available to console
    video.srcObject = stream;
    // Refresh button list in case labels have become available
    return navigator.mediaDevices.enumerateDevices();
  }

  function start() {
    if (window.stream) {
      window.stream.getTracks().forEach(function (track) {
        track.stop();
      });
    }
    var videoSource = videoSelect.value;
    var constraints = {
      video: {
        deviceId: videoSource ? { exact: videoSource } : undefined
      }
    };
    navigator.mediaDevices
      .getUserMedia(constraints)
      .then(gotStream)
      .then(gotDevices)
      .catch(handleError);
  }

  videoSelect.onchange = start;

  function handleError(error) {
    console.log("navigator.getUserMedia error: ", error);
  }

  start();
})