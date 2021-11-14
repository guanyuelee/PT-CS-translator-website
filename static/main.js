// Credit: https://codepen.io/t7team/pen/ZowdRN
function openTab(e, tabName) {
    let i, x, tabLinks;
    x = document.getElementsByClassName('content-tab');
    for (i = 0; i < x.length; i++) {
        x[i].style.display = 'none';
    }
    tabLinks = document.getElementsByClassName('tab');
    for (i = 0; i < x.length; i++) {
        tabLinks[i].className = tabLinks[i].className.replace(' is-active', '');
    }
    document.getElementById(tabName).style.display = 'block';
    e.className += ' is-active';
}

function submitSrcImage() {
    let srcImage = document.getElementById("srcImage");
    srcImage.click();
    srcImage.onchange = function (e) {
        let image = srcImage.files[0];
        if (image) {
            document.getElementById('showSrcImage').src = URL.createObjectURL(image);
        }

    }
}

function submitRefImage() {
    let refImage = document.getElementById("refImage");
    refImage.click();
    refImage.onchange = function (e) {
        let image = refImage.files[0];
        if (image) {
            document.getElementById('showRefImage').src = URL.createObjectURL(image);
        }

    }
}

async function StarGANv2Generate() {
    let form = new FormData();
    let y = document.getElementById('y').value;
    let seed = document.getElementById('seed').value;
    let isRef = document.getElementById("refRadio").checked;
    let mode = "latent";
    if (isRef) mode = "reference"
    let src_img = document.getElementById("srcImage").files[0];
    if (isRef) {
        let ref_img = document.getElementById("refImage").files[0];
        form.append("ref_img", ref_img, "ref_img");
    }
    form.append("model", "starganv2_afhq");
    form.append("y", y);
    form.append("seed", seed);
    form.append("mode", mode);
    form.append("src_img", src_img, "src_img");
    let res = await fetch("/api/model", {
        method: 'post',
        body: form
    });
    let data = await res.json();
    if (data.success) {
        document.getElementById('showResImage').src = "/" + data.data[0];
    } else {
        showErrorMessage(data.message);
    }
}


function showErrorMessage(message, duration = 5) {
    console.error(message);
    let e = document.getElementById('errorMessage');
    e.children[0].textContent = `Error: ${message}`;
    e.style.display = 'block';
    setTimeout(() => {
        e.style.display = 'none';
    }, duration * 1000);
}

/**调用open打开录音请求好录音权限**/
function recOpen(id, id_label){//一般在显示出录音按钮或相关的录音界面时进行此方法调用，后面用户点击开始录音时就能畅通无阻了
	rec=null;
	recBlob=null;
	var newRec=Recorder({
		type:"mp3",sampleRate:16000,bitRate:16 //mp3格式，指定采样率hz、比特率kbps，其他参数使用默认配置；注意：是数字的参数必须提供数字，不要用字符串；需要使用的type类型，需提前把格式支持文件加载进来，比如使用wav格式需要提前加载wav.js编码引擎
		,onProcess:function(buffers,powerLevel,bufferDuration,bufferSampleRate,newBufferIdx,asyncEnd){
			//录音实时回调，大约1秒调用12次本回调
			document.querySelector(".recpowerx").style.width=powerLevel+"%";
			document.querySelector(".recpowert").innerText=(bufferDuration/1000).toFixed(2) + " sec";
		}
	});

	newRec.open(function(){//打开麦克风授权获得相关资源
		rec=newRec;
		//此处创建这些音频可视化图形绘制浏览器支持妥妥的
		console.log("已打开录音，可以点击录制开始录音了");
        document.getElementById(id).className = "button is-success";
        document.getElementById(id).innerHTML = "录音权限成功";
        document.getElementById(id_label).innerHTML = "成功调用录音功能，请继续！";
        document.getElementById(id).disabled = "true";

	},function(msg,isUserNotAllow){//用户拒绝未授权或不支持
		console.log((isUserNotAllow?"UserNotAllow，":"") + "打开录音失败："+msg);
        document.getElementById(id).className = "button is-danger";
        document.getElementById(id).innerHTML = "录音权限失败";
        document.getElementById(id_label).innerHTML = "需要您允许录音功能，请刷新页面重试。";
	});
	
	window.waitDialogClick=function(){
		console.log("打开失败：权限请求被忽略，<span style='color:#f00'>用户主动点击的弹窗</span>");
	};
};

/**关闭录音，释放资源**/
function recClose(){
	if(rec){
		rec.close();
		console.log("已关闭");
	}else{
		console.log("未打开录音");
	};
};

/**开始录音**/
function recStart(id_start, id_stop, id_play, id_upload){//打开了录音后才能进行start、stop调用
	if(rec&&Recorder.IsOpen()){
		recBlob=null;
		rec.start();
        document.getElementById(id_start).disabled = true;
        document.getElementById(id_stop).disabled = false;
        document.getElementById(id_play).disabled = true;
        document.getElementById(id_upload).disabled = true;
		console.log("已开始录音...");
	}else{
		console.log("未打开录音");
	};
};

/**暂停录音**/
function recPause(){
	if(rec&&Recorder.IsOpen()){
		rec.pause();
	}else{
		console.log("未打开录音");
	};
};
/**恢复录音**/
function recResume(){
	if(rec&&Recorder.IsOpen()){
		rec.resume();
	}else{
		console.log("未打开录音");
	};
};

/**结束录音，得到音频文件**/
function recStop(id_start, id_stop, id_play, id_upload){
	if(!(rec&&Recorder.IsOpen())){
		console.log("未打开录音");
		return;
	};
	rec.stop(function(blob,duration){
		console.log(blob,(window.URL||webkitURL).createObjectURL(blob),"时长:"+duration+"ms");
		recBlob=blob;
        document.getElementById(id_start).disabled = false;
        document.getElementById(id_stop).disabled = true;
        document.getElementById(id_play).disabled = false;
        document.getElementById(id_upload).disabled = false;
		console.log("已录制mp3："+duration+"ms "+blob.size+"字节，可以点击播放、上传了");
	},function(msg){
		console.log("录音失败:"+msg);
	});
};

/**播放**/
function recPlay(){
	if(!recBlob){
		console.log("请先录音，然后停止后再播放");
		return;
	};

	var cls=("a"+Math.random()).replace(".","");
    document.getElementById("ph_span").innerHTML='<span class="'+cls+'"></span>';
	console.log('播放中: ' + cls);
	var audio=document.createElement("audio");
	audio.controls=true;
	document.querySelector("."+cls).appendChild(audio);
	//简单利用URL生成播放地址，注意不用了时需要revokeObjectURL，否则霸占内存
	audio.src=(window.URL||webkitURL).createObjectURL(recBlob);
	audio.play();
	
	setTimeout(function(){
		(window.URL||webkitURL).revokeObjectURL(audio.src);
	},5000);
};

/**上传**/
async function recUpload(id_start, id_stop, id_play, id_upload){
	var blob=recBlob;
	if(!blob){
		console.log("请先录音，然后停止后再上传");
		return;
	};

    // 将所有的按钮都不可选用，等待成功后新一组进行翻译
    document.getElementById(id_start).disabled = true;
    document.getElementById(id_stop).disabled = true;
    document.getElementById(id_play).disabled = true;
    document.getElementById(id_upload).disabled = true;
	
	//本例子假设使用原始XMLHttpRequest请求方式，实际使用中自行调整为自己的请求方式
	//录音结束时拿到了blob文件对象，可以用FileReader读取出内容，或者用FormData上传

	/***方式二：使用FormData用multipart/form-data表单上传文件***/

    let isFemale_ratio = document.getElementById("label_female");
    gender = "male"
    if(isFemale_ratio.checked) gender = "female";
    let which_region = document.getElementById('select_region');
    var index=which_region.selectedIndex;
    let region = which_region.options[index].text;
    let email_input = document.getElementById('email_input');
    email = "xx@xx";
    if(email_input.value) email = email_input.value;
    
    condition = false;
    let condition_checkbox = document.getElementById('condition_checkbox');
    if (condition_checkbox.checked) condition = true;

    console.log(gender, region, email, condition);

    var form=new FormData();
	form.append("upfile", blob, "recorder.mp3"); //和普通form表单并无二致，后端接收到upfile参数的文件，文件名为recorder.mp3
    form.append("gender", gender);
    form.append("region", region);
    form.append("email", email);
    form.append("condition", condition);
    form.append("next_sentence", next_sentence);
    form.append("next_sentence_file_name", next_sentence_file_name);
    form.append("n_translations", n_translations);
    form.append("which_sentence", which_sentence)

    let res = await fetch("/api/upload", {
        method: 'post',
        body: form
    });
    let data = await res.json();
    if (data.success) {
        console.log(data)
        next_sentence = data.next_sentence;
        next_sentence_file_name = data.next_sentence_file_name
        document.getElementById("label_translation_text").innerHTML = n_translations + "、 " + data.next_sentence;
        document.getElementById("label_count_translations").innerHTML = data.count_translations;
    } else {
        document.getElementById("label_translation_text").innerHTML = "出现错误，无法上传服务器";
    }
	//...其他表单参数
    
    document.getElementById(id_start).disabled = false;
    document.getElementById(id_stop).disabled = true;
    document.getElementById(id_play).disabled = true;
    document.getElementById(id_upload).disabled = true;
    n_translations += 1;
};

function display(id){
    var target = document.getElementById(id);
    if(target.style.display=="none"){
        target.style.display="";
    }else{
        target.style.display="none";
    }
}