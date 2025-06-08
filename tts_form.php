<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['ajax']) && $_POST['ajax']==='1') {
    header('Content-Type: application/json; charset=UTF-8');
    $python_path = "python";
    $script_path = __DIR__ . DIRECTORY_SEPARATOR . "your_tts.py";
    $text  = isset($_POST['tts_text']) ? trim($_POST['tts_text']) : '';
    $voice = isset($_POST['voice']) ? $_POST['voice'] : 'fable';

    if ($text === '') {
        echo json_encode(['error'=>'請輸入文字！']); exit;
    }

    $filename = 'tts_' . uniqid() . '.mp3';
    $full_path = __DIR__ . DIRECTORY_SEPARATOR . 'tts_tmp' . DIRECTORY_SEPARATOR . $filename;

    $cmd = sprintf('%s %s %s %s %s 2>&1',
        $python_path,
        escapeshellarg($script_path),
        escapeshellarg($text),
        escapeshellarg($voice),
        escapeshellarg($full_path)
    );
    exec($cmd, $output, $ret);

    if ($ret != 0 || !file_exists($full_path)) {
    $py_error = htmlspecialchars(implode("\n", $output));
    echo json_encode([
        'error' => "產生語音失敗，詳細資訊如下：<br><pre style='font-size:12px;color:#fff;background:#b12;padding:10px;'>$py_error</pre>"
    ]);
    exit;
    }

    echo json_encode([
        'success'=>1,
        'mp3' => "tts_tmp/" . $filename,
    ]);
    exit;
}
?><!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OpenAI TTS 語音合成表單</title>
    <style>
        body {background: #f7f7f9; font-family: Arial,sans-serif; margin:0; padding:0;}
        .container {
            min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .center-box {
            background:#fff; padding:30px 40px; border-radius:12px; box-shadow:0 4px 16px rgba(0,0,0,0.09);
            min-width:340px; max-width:700px; text-align:center;
        }
        textarea { width:100%; max-width:600px; min-width:250px; margin-bottom:12px; font-size:16px; border-radius:6px; border:1px solid #aaa; padding:8px;}
        select{font-size:16px; border-radius:6px; border:1px solid #aaa; margin-bottom:12px; padding:6px 10px;}
        input[type=submit]{
            font-size:16px; background:#1867c0; color:#fff; border:none; border-radius:6px; padding:10px 25px; margin-top:6px;
            cursor:pointer; transition:background 0.2s;
        }
        input[type=submit]:hover{background:#134e96;}
        .err{color:#fff; background:#c0392b; padding:8px 14px; border-radius:7px; margin-bottom:14px;}
        .output-label {margin-top:20px; color:#444; font-size:17px; font-weight:bold;}
        audio{margin-top:10px; width:94%;}
        /* spinner overlay */
        #spinner-overlay {
            position: fixed; left:0; top:0; width:100vw; height:100vh; background:rgba(255,255,255,0.7);
            display:none; z-index: 4200;justify-content: center; align-items: center;
        }
        .lds-ring {display: inline-block; position: relative; width: 80px; height: 80px;}
        .lds-ring div {
            box-sizing: border-box;
            display: block;
            position: absolute;
            width: 64px;
            height: 64px;
            margin: 8px;
            border: 8px solid #1867c0;
            border-radius: 50%;
            border-color: #1867c0 transparent transparent transparent;
            animation: lds-ring 1s cubic-bezier(0.5, 0, 0.5, 1) infinite;
        }
        .lds-ring div:nth-child(1) {animation-delay: -0.45s;}
        .lds-ring div:nth-child(2) {animation-delay: -0.3s;}
        .lds-ring div:nth-child(3) {animation-delay: -0.15s;}
        @keyframes lds-ring {
            0% {transform: rotate(0deg);}
            100% {transform: rotate(360deg);}
        }
    </style>
</head>
<body>
<div class="container">
    <div class="center-box">
        <h2>OpenAI TTS Demo</h2>
        <form id="tts-form" method="post" action="">
            <textarea name="tts_text" rows="20" placeholder="請輸入要轉換的文字" id="tts_text"></textarea><br>
            <select name="voice" id="voice">
                <option value="fable">Fable（女）</option>
                <option value="shimmer">Shimmer（女）</option>
                <option value="nova">Nova（女）</option>
                <option value="alloy">Alloy（男）</option>
                <option value="onyx">Onyx（男）</option>
            </select>
            <br>
            <input type="submit" value="產生語音並播放">
            <div id="err-msg"></div>
            <div id="output-box"></div>
        </form>
    </div>
</div>
<div id="spinner-overlay">
    <div class="lds-ring"><div></div><div></div><div></div><div></div></div>
</div>
<script>
document.getElementById('tts-form').onsubmit = function(e){
    e.preventDefault();
    document.getElementById('err-msg').innerHTML = "";
    document.getElementById('output-box').innerHTML = "";
    document.getElementById('spinner-overlay').style.display = "flex";

    const formData = new FormData(this);
    formData.append('ajax', '1');
    fetch('', {
        method: 'POST',
        body: formData,
    })
    .then(resp => resp.json())
    .then(j => {
        document.getElementById('spinner-overlay').style.display = "none";
        if(j.error){
            document.getElementById('err-msg').innerHTML = '<div class="err">'+j.error+'</div>';
            return;
        }
        let output = '<div class="output-label">生成語音如下：</div><audio controls autoplay src="'+j.mp3+'"></audio>';
        document.getElementById('output-box').innerHTML = output;
    })
    .catch(err => {
        document.getElementById('spinner-overlay').style.display = "none";
        document.getElementById('err-msg').innerHTML = '<div class="err">網路錯誤，請重新嘗試！</div>';
    });
}
</script>
</body>
</html>
