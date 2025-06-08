<?php
// 是否有資料
if (!isset($_POST['tts_text']) || trim($_POST['tts_text']) == '') {
    die('請輸入文字！');
}

$text = $_POST['tts_text'];
$voice = isset($_POST['voice']) ? $_POST['voice'] : 'fable';

// 產生unique檔名
$filename = 'tts_' . uniqid() . '.mp3';
$full_path = __DIR__ . DIRECTORY_SEPARATOR . 'tts_tmp' . DIRECTORY_SEPARATOR . $filename;

// 組 python 指令
$escaped_text = escapeshellarg($text);
$escaped_voice = escapeshellarg($voice);
$escaped_out = escapeshellarg($full_path);

// PHP執行路徑要加上 full path
$python_path = "python";  // 或填完整路徑，如 "C:\\Python312\\python.exe"
$script_path = __DIR__ . DIRECTORY_SEPARATOR . "your_tts.py";
$script_path = escapeshellarg($script_path); // 也escape防中文目錄

$cmd = "$python_path $script_path $escaped_text $escaped_voice $escaped_out 2>&1"; // 將執行訊息丟到標準輸出

// 執行並取得log
exec($cmd, $output, $ret);

// 顯示 error log 區塊
// echo "<pre style='border:1px solid #aaa; color:#444; background:#f4f4f4;'>";
// echo "PY-CMD: $cmd\n";
// echo "RET: $ret\n";
// echo "OUTPUT:\n";
// echo htmlspecialchars(implode("\n",$output));
// echo "</pre>";

if ($ret != 0 || !file_exists($full_path)) {
    die("產生語音失敗或無法保存音檔！");
}

?>

<html>
<head><title>TTS 播放結果</title></head>
<body>
<h2>生成語音如下：</h2>
<audio controls src="tts_tmp/<?php echo $filename ?>" ></audio>
<br>
<a href="tts_form.php">返回上一頁</a>
</body>
</html>