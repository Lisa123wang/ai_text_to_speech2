<?php
// 顯示錯誤方便偵錯
ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(E_ALL);
// 不限執行時間
set_time_limit(0);
ini_set('max_execution_time', 0);

// 處理 AJAX 請求
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['ajax'] ?? '') === '1') {
    header('Content-Type: application/json; charset=UTF-8');

    // 1️⃣ 讀使用者輸入
    $text  = trim($_POST['tts_text'] ?? '');
    $voice = $_POST['voice'] ?? 'fable';
    if ($text === '') {
        echo json_encode(['error'=>'請輸入文字！']);
        exit;
    }

    // 2️⃣ 建暫存資料夾 & 寫文字檔
    $tmpDir = __DIR__ . '/tts_tmp';
    if (!is_dir($tmpDir)) {
        mkdir($tmpDir, 0755, true);
    }
    $inputFile = "$tmpDir/input_" . uniqid() . ".txt";
    file_put_contents($inputFile, $text);

    // 3️⃣ 準備輸出 MP3 路徑
    $filename   = "tts_" . uniqid() . ".mp3";
    $outputFile = "$tmpDir/$filename";

    // 4️⃣ **這裡改成傳 $inputFile 而不是 $text** **
    $python = 'python';   // 或 '/usr/bin/python3'
    $script = __DIR__ . '/your_tts.py';
    $cmd = sprintf(
        '%s %s %s %s %s 2>&1',
        $python,
        escapeshellarg($script),
        escapeshellarg($inputFile),   // ← 传文件路径
        escapeshellarg($voice),
        escapeshellarg($outputFile)
    );
    exec($cmd, $output, $ret);

    // 5️⃣ 失敗後回傳完整 Debug 資訊
    if ($ret !== 0 || !file_exists($outputFile)) {
        echo json_encode([
            'error' => '產生語音失敗，請查看 debug',
            'debug' => [
                'cmd'      => $cmd,
                'ret_code' => $ret,
                'output'   => $output,
                'exists'   => file_exists($outputFile) ? 'yes' : 'no',
            ],
        ]);
        exit;
    }

    // 6️⃣ 成功，回傳播放路徑
    echo json_encode([
        'success' => 1,
        'mp3'     => "tts_tmp/$filename",
    ]);
    exit;
}

?>
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <title>OpenAI TTS Demo</title>
  <style>
    body { background:#f7f7f9; font-family:Arial,sans-serif; margin:0; padding:0 }
    .container { min-height:100vh; display:flex; justify-content:center; align-items:center }
    .box { background:#fff; padding:30px; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1); width:90%; max-width:600px; text-align:center }
    textarea { width:100%; height:150px; margin-bottom:6px; padding:8px; font-size:16px; border:1px solid #aaa; border-radius:6px; resize:vertical }
    .stats { text-align:left; font-size:14px; color:#555; margin-bottom:12px; min-height:1.2em }
    select { font-size:16px; padding:6px 10px; margin-bottom:12px; border:1px solid #aaa; border-radius:6px }
    input[type=submit] { font-size:16px; padding:10px 25px; background:#1867c0; color:#fff; border:none; border-radius:6px; cursor:pointer; transition:background .2s }
    input[type=submit]:hover { background:#134e96 }
    .err { background:#c0392b; color:#fff; padding:8px 14px; border-radius:7px; margin:10px 0 }
    .output-label { margin-top:20px; font-size:17px; font-weight:bold; color:#444 }
    audio { margin-top:10px; width:94% }
    #spinner-overlay { position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(255,255,255,.7); display:none; z-index:999; justify-content:center; align-items:center }
    .lds-ring { display:inline-block; position:relative; width:80px; height:80px }
    .lds-ring div { box-sizing:border-box; display:block; position:absolute; width:64px; height:64px; margin:8px; border:8px solid #1867c0; border-radius:50%; border-color:#1867c0 transparent transparent transparent; animation:lds-ring 1s cubic-bezier(.5,0,.5,1) infinite }
    .lds-ring div:nth-child(1) { animation-delay:-.45s }
    .lds-ring div:nth-child(2) { animation-delay:-.3s }
    .lds-ring div:nth-child(3) { animation-delay:-.15s }
    @keyframes lds-ring { to { transform:rotate(360deg) } }
  </style>
</head>
<body>
<div class="container">
  <div class="box">
    <h2>OpenAI TTS Demo</h2>
    <form id="tts-form" method="post">
      <textarea name="tts_text" id="tts_text" placeholder="請輸入要合成的文字…"></textarea>
      <div id="stats-box" class="stats"></div>
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
// 自述統計
const ta = document.getElementById('tts_text'),
      sb = document.getElementById('stats-box');
function updateStats(){
  const t = ta.value;
  const c = t.length;
  const w = t.trim()? t.trim().split(/\s+/).length:0;
  const s = t.split(/[。！？!?]/).filter(x=>x.trim()).length;
  sb.textContent = `字元：${c}，單詞：${w}，句子：${s}`;
}
ta.addEventListener('input',updateStats);
updateStats();

// 處理提交
document.getElementById('tts-form').onsubmit = function(e){
  e.preventDefault();
  document.getElementById('err-msg').innerHTML='';
  document.getElementById('output-box').innerHTML='';
  document.getElementById('spinner-overlay').style.display='flex';

  const fd = new FormData(this);
  fd.append('ajax','1');

  fetch('',{ method:'POST', body:fd })
    .then(r=>r.json())
    .then(j=>{
      document.getElementById('spinner-overlay').style.display='none';
      if(j.error){
        document.getElementById('err-msg').innerHTML=`<div class="err">${j.error}</div>`;
      } else {
        document.getElementById('output-box').innerHTML =
          '<div class="output-label">生成語音如下：</div>'+
          `<audio controls autoplay src="${j.mp3}"></audio>`;
      }
    })
    .catch(_=>{
      document.getElementById('spinner-overlay').style.display='none';
      document.getElementById('err-msg').innerHTML=`<div class="err">網路錯誤，請重試！</div>`;
    });
};
</script>
</body>
</html>
