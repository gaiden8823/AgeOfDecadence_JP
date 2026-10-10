param([ValidateSet('menu','check','install','restore','font')][string]$Mode='menu',[string]$FontName)
$ErrorActionPreference='Stop'
$Game=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
$Utf8=New-Object Text.UTF8Encoding($false)
function SafePath($Root,$Relative) {
 if ([IO.Path]::IsPathRooted($Relative)) { throw "Unsafe path: $Relative" }
 $r=[IO.Path]::GetFullPath($Root).TrimEnd('\')
 $p=[IO.Path]::GetFullPath((Join-Path $r $Relative))
 if (!$p.StartsWith($r+'\',[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe path: $Relative" }
 if ($p.Length -ge 260) { throw 'パスが長すぎます。ゲーム・試験用フォルダを短い場所に配置してください。' }
 # Never traverse directory junctions or symbolic links.
 $walk=$p
 while ($walk.Length -ge $r.Length) {
  if (Test-Path -LiteralPath $walk) {
   if ((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked path: $walk" }
  }
  $walk=Split-Path -Parent $walk
  if (!$walk) { break }
 }
 return $p
}
function Hash($p) {
 $stream=[IO.File]::OpenRead($p)
 $sha=[Security.Cryptography.SHA256]::Create()
 try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
 finally { $stream.Dispose(); $sha.Dispose() }
}
function WriteJson($p,$obj) { [IO.File]::WriteAllText($p,($obj | ConvertTo-Json -Depth 12),$Utf8) }
function Closed {
 if (Get-Process -Name AoD,AoD64 -ErrorAction SilentlyContinue) { throw 'ゲームを終了してください。' }
}
function CopyFile($src,$dst) {
 [IO.Directory]::CreateDirectory((Split-Path -Parent $dst)) | Out-Null
 [IO.File]::Copy($src,$dst,$true)
}
function Latest {
 $dirs=@(Get-ChildItem -LiteralPath (Join-Path $Game '.aodjp_backups') -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending)
 foreach ($d in $dirs) {
  $p=SafePath $Game ('.aodjp_backups/'+$d.Name+'/restore.json')
  if (Test-Path -LiteralPath $p) {
   $s=Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json
   if (!$s.restored) { return @{dir=$d.FullName; state=$s; path=$p} }
  }
 }
 throw '有効なバックアップがありません。'
}
function ValidateState($b) {
 if ($b.state.game -ne $Game) { throw 'バックアップのゲームフォルダが違います。' }
 foreach ($r in $b.state.files) {
  $p=SafePath $Game $r.path
  if (!(Test-Path -LiteralPath $p -PathType Leaf) -or (Hash $p) -ne $r.installed) { throw "導入後に変更されたファイル: $($r.path)" }
  if ($r.existed) {
   $o=SafePath (Join-Path $b.dir 'original') $r.path
   if ((Hash $o) -ne $r.original) { throw "バックアップ破損: $($r.path)" }
  }
 }
}
function SelectFont {
 Add-Type -AssemblyName System.Drawing
 $folder=Join-Path $PSScriptRoot 'fonts'
 $files=@(Get-ChildItem -LiteralPath $folder -File | Where-Object { $_.Extension.ToLowerInvariant() -in '.ttf','.otf','.ttc' } | Sort-Object Name)
 if (!$files.Count) {
  $p=Join-Path $env:WINDIR 'Fonts\BIZ-UDMinchoM.ttc'
  if (!(Test-Path -LiteralPath $p -PathType Leaf)) { throw '標準フォントがありません。AoDJP/fonts に日本語フォントを置いてください。' }
  return @{name='BIZ UDPMincho Medium'; file=$p.Replace('\','/')}
 }
 $options=@()
 foreach ($f in $files) {
  $p=SafePath $folder $f.Name
  $collection=New-Object Drawing.Text.PrivateFontCollection
  try {
   $collection.AddFontFile($p)
   foreach ($family in $collection.Families) { $options+=@{name=$family.Name; file=$p.Replace('\','/'); label=($f.Name+' / '+$family.Name)} }
  } catch { Write-Warning "読み込めないフォント: $($f.Name)" }
  finally { $collection.Dispose() }
 }
 if (!$options.Count) { throw '読み込めるフォントがありません。' }
 if ($FontName) {
  $matches=@($options | Where-Object { $_.name -eq $FontName })
  if ($matches.Count -ne 1) { throw '指定フォントを一意に選べません。' }
  return $matches[0]
 }
 if ($options.Count -eq 1) { return $options[0] }
 for ($i=0;$i -lt $options.Count;$i++) { Write-Host "$($i+1): $($options[$i].label)" }
 $n=0
 if (![int]::TryParse((Read-Host 'フォント番号'),[ref]$n) -or $n -lt 1 -or $n -gt $options.Count) { throw '選択を中止しました。' }
 return $options[$n-1]
}
function FontBytes($rel,$font) {
 $src=SafePath (Join-Path $PSScriptRoot 'payload') $rel
 $text=[IO.File]::ReadAllText($src,$Utf8)
 if ($text.Contains('BIZ UDPMincho Medium') -or $text.Contains('C:/Windows/Fonts/BIZ-UDMinchoM.ttc')) {
  if ($font.name -match '["\\<>:\r\n]' -or $font.file -match '["\r\n]') { throw 'フォント名・パスに使用できない文字があります。' }
  $text=$text.Replace('BIZ UDPMincho Medium',$font.name).Replace('C:/Windows/Fonts/BIZ-UDMinchoM.ttc',$font.file)
  return ,$Utf8.GetBytes($text)
 }
 return ,([IO.File]::ReadAllBytes($src))
}
try {
 if (!(Test-Path -LiteralPath (Join-Path $Game 'AoD.exe') -PathType Leaf)) { throw '日本語化.cmd と AoDJP を AoD.exe と同じフォルダに配置してください。' }
 $manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
 if ($Mode -eq 'menu') {
  Write-Host '日本語化MOD: 1 確認 / 2 導入 / 3 元に戻す / 4 フォント変更 / その他 終了'
  switch (Read-Host '番号') { '1' {$Mode='check'} '2' {$Mode='install'} '3' {$Mode='restore'} '4' {$Mode='font'} default {exit 0} }
 }
 # Verify shipped files even when only changing the font.
 foreach ($r in $manifest.files) {
  if ((Hash (SafePath (Join-Path $PSScriptRoot 'payload') $r.path)) -ne $r.sha256) { throw "配布ファイル破損: $($r.path)" }
 }
 if ($Mode -eq 'restore') {
  Closed
  $b=Latest
  ValidateState $b
  foreach ($r in @($b.state.files)[($b.state.files.Count-1)..0]) {
   $p=SafePath $Game $r.path
   if ($r.existed) { CopyFile (SafePath (Join-Path $b.dir 'original') $r.path) $p }
   else { Remove-Item -LiteralPath $p }
  }
  $b.state.restored=$true
  WriteJson $b.path $b.state
  Write-Host '復元しました。バックアップと交換用フォントは保持しています。'
  exit 0
 }
 if ($Mode -eq 'font') {
  Closed
  $b=Latest
  if ($b.state.version -ne $manifest.version) { throw '導入済みMODとツールの版が違います。' }
  ValidateState $b
  $font=SelectFont
  $changed=@()
  try {
   foreach ($r in $b.state.files) {
    if ($r.path.EndsWith('.cs')) {
     $src=SafePath (Join-Path $PSScriptRoot 'payload') $r.path
     if ([IO.File]::ReadAllText($src,$Utf8).Contains('BIZ UDPMincho Medium')) {
      $p=SafePath $Game $r.path
      $changed+=@{p=$p; bytes=[IO.File]::ReadAllBytes($p); record=$r; hash=$r.installed}
      [IO.File]::WriteAllBytes($p,(FontBytes $r.path $font))
      $r.installed=Hash $p
     }
    }
   }
   $b.state.font=$font.name
   WriteJson $b.path $b.state
  } catch {
   foreach ($c in $changed) { [IO.File]::WriteAllBytes($c.p,$c.bytes); $c.record.installed=$c.hash }
   throw
  }
  Write-Host "フォントを変更しました: $($font.name)。ゲームを再起動してください。"
  exit 0
 }
 foreach ($r in $manifest.baseline_archives) {
  if ((Hash (SafePath $Game $r.path)) -ne $r.sha256) { throw "対応ゲーム版ではありません: $($r.path)" }
 }
 foreach ($r in $manifest.files) {
  $p=SafePath $Game $r.path
  if (Test-Path -LiteralPath $p) {
   if (!$r.baseline_sha256 -or (Hash $p) -ne $r.baseline_sha256) { throw "既存MOD・変更との競合: $($r.path)。旧版を復元してから導入してください。" }
  } elseif ($r.baseline_sha256) { throw "元ファイル不足: $($r.path)" }
 }
 $font=SelectFont
 Write-Host "確認成功: $($manifest.files.Count) ファイル / フォント: $($font.name)"
 if ($Mode -eq 'check') { exit 0 }
 Closed
 $backup=SafePath $Game ('.aodjp_backups/'+(Get-Date -Format 'yyyyMMdd_HHmmss_fffffff'))
 [IO.Directory]::CreateDirectory($backup) | Out-Null
 $records=@()
 foreach ($r in $manifest.files) {
  $p=SafePath $Game $r.path
  $exists=Test-Path -LiteralPath $p -PathType Leaf
  $hash=$null
  if ($exists) { $hash=Hash $p; CopyFile $p (SafePath (Join-Path $backup 'original') $r.path) }
  $records+=[pscustomobject]@{path=$r.path; installed=$r.sha256; existed=$exists; original=$hash}
 }
 $state=[pscustomobject]@{game=$Game;version=$manifest.version;restored=$false;font=$font.name;files=$records}
 $done=@()
 try {
  foreach ($r in $records) {
   $p=SafePath $Game $r.path
   [IO.Directory]::CreateDirectory((Split-Path -Parent $p)) | Out-Null
   $done+=$r
   if ($r.path.EndsWith('.cs')) { [IO.File]::WriteAllBytes($p,(FontBytes $r.path $font)) }
   else { CopyFile (SafePath (Join-Path $PSScriptRoot 'payload') $r.path) $p }
   $r.installed=Hash $p
  }
  WriteJson (Join-Path $backup 'restore.json') $state
 } catch {
  [array]::Reverse($done)
  foreach ($r in $done) {
   $p=SafePath $Game $r.path
   if ($r.existed) { CopyFile (SafePath (Join-Path $backup 'original') $r.path) $p }
   elseif (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p }
  }
  throw
 }
 Write-Host "導入しました。バックアップ: $backup"
 Write-Host 'ゲームの言語一覧で「日本語」を選んでください。'
} catch { Write-Host $_.Exception.Message -ForegroundColor Red; exit 1 }
