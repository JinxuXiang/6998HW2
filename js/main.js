//import * as AWS from 'aws-sdk';
/*** Connect with API Gateway ***/
var apigClient = apigClientFactory.newClient();

var albumBucketName = "6998hw2";
var transcribeBucketName = "6998hw2";
var bucketRegion = "us-east-1";
var IdentityPoolId = "us-east-1:12dcf442-0937-4a60-aa98-2cb5d7d955b3";
var random_str_audio = Math.random().toString(36).slice(-6)

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
	IdentityPoolId: IdentityPoolId
  })
});

var s3 = new AWS.S3({
  apiVersion: "2006-03-01",
  params: { Bucket: albumBucketName }
});

function showImage(src, width, height, alt) {
	var img = document.createElement("img");
	img.src = src;
	img.width = width;
	img.height = height;
	img.alt = alt;
};


// upload photos
apigClient = apigClientFactory.newClient();
$(document).ready(function(){
  $("#but_upload").click(function(){
	

	function addPhoto() {
		var files  = $("#file").prop('files')
		if (!files.length) {
			return alert("Please choose a file to upload first.");
		}
		var file = files[0];
		var fileName = file.name;
		var albumPhotosKey = encodeURIComponent('Photo') + "/";
		var albumLabelsKey = encodeURIComponent('Label') + "/";
		
		var random_str = Math.random().toString(36).slice(-6)
		var photoKey = albumPhotosKey + fileName.split(".")[0] + '_' + random_str + '.' + fileName.split(".")[1];
		var labelKey = albumLabelsKey + fileName.split(".")[0] + '_' + random_str +  ".txt";
		console.log(photoKey)
		// Use S3 ManagedUpload class as it supports multipart uploads
		var upload = new AWS.S3.ManagedUpload({
			params: {
			  Bucket: albumBucketName,
			  Key: photoKey,
			  Body: file
			}
		});
		if ($('#label').val()){
			console.log($('#label').val())
			var upload_label = new AWS.S3.ManagedUpload({
				params: {
				Bucket: albumBucketName,
				Key: labelKey,
				Body: $('#label').val()
				}
			});
			var promise_label = upload_label.promise();
		}
		var promise = upload.promise();
		

		promise.then(
			function(data) {
			  alert("Successfully uploaded photo.");
			},
			function(err) {
			  return alert("There was an error uploading your photo: ", err.message);
			}
		);
	};
	addPhoto('Photo');

	});
}); 

var rec=Recorder({
	bitRate:32,
	sampleRate:24000
	});


record.onclick = e => {
	console.log('I was clicked record')
	record.disabled = true;
	record.style.backgroundColor = "blue"
	stopRecord.disabled=false;
	audioSearch.disabled=true;

	rec.open(function(){
		rec.start();
	},function(msg,isUserNotAllow){
		console.log((isUserNotAllow?"UserNotAllow，":"")+"can't record:"+msg);
	});
}

stopRecord.onclick = e => {
	console.log("I was clicked stop")
	record.disabled = false;
	stopRecord.disabled=true;
	audioSearch.disabled=false;

	record.style.backgroundColor = "red"
	rec.stop(function(blob,duration){
		console.log(URL.createObjectURL(blob),"Duration:"+duration+"ms");
		console.log('Audio:', blob);
		rec.close();
		var audio=document.createElement("audio");
		audio.controls=true;
		document.body.appendChild(audio);
		audio.src=URL.createObjectURL(blob);
		// audio.play();
		console.log(audio.src)

		random_str_audio = Math.random().toString(36).slice(-6)
		var audioKey = 'Audio/' + random_str_audio + '.mp3'
		console.log(audioKey)
		var upload_audio = new AWS.S3.ManagedUpload({
			params: {
			Bucket: albumBucketName,
			Key: audioKey,
			Body: blob
			}
		});
		var promise_audio = upload_audio.promise();

		

		
		/*
		var audio_uri = 'https://s3.amazonaws.com/' + albumBucketName + '/' + audioKey;
		console.log(audio_uri);
		var transcribeService = new AWS.TranscribeService();

		// Set the parameters
		const params = {
			TranscriptionJobName: transcribeBucketName,
			LanguageCode: "en-US", // For example, 'en-US'
			MediaFormat: "mp3", // For example, 'wav'
			Media: {
				MediaFileUri: audio_uri,
				// For example, "https://transcribe-demo.s3-REGION.amazonaws.com/hello_world.wav"
			},
			OutputBucketName: transcribeBucketName
		};
		console.log(params)
		var promise_tran = transcribeService.startTranscriptionJob(params).promise()
		promise_tran.then(
			function(data) {
				console.log(data)
			  	alert("Successfully transcribe.");
			},
			function(err) {
			  return alert("There was an error transcribing audio: ", err.message);
			}
		);
		console.log('Finish Transcription');
		*/

		
		
		
	});
}

audioSearch.onclick = e => {
	console.log('I was clicked audio search')

	console.log('wait');
	var params = {Bucket: albumBucketName, Key: random_str_audio + '.json'}
	new AWS.S3().getObject(params, function(err, data)
	{
		if (!err)
			var s3file = data.Body.toString()
			s3file = JSON.parse(s3file)
			console.log(s3file)
			console.log(s3file["results"]["transcripts"][0]["transcript"])
			document.getElementById("searchin").value = s3file["results"]["transcripts"][0]["transcript"]
	});
}


// after clcik the search button, show the search result
$('#btngo').click(function(){
	document.getElementById("show").innerHTML = ""
	console.log("Search was clicked")
	var query = $('#searchin').val();
	console.log(query)
	var params = {q: query};
	apigClient.searchGet(params, {}, {})
		.then(function(result){
		//This is where you would put a success callback
		console.log(result);
		// 这里写showImage的函数
		let img_list = result.data
		for (var i = 0; i < img_list.length; i++) {
			var img_url = img_list[i];
			var new_img = document.createElement('img');
			new_img.src = img_url;
			new_img.width = 500;
			document.getElementById("show").appendChild(new_img);
		}
		
		}).catch(function(result){
		//This is where you would put an error callback
		console.log(result);
		});

});