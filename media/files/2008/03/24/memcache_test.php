<?php
$link = mysql_connect('127.0.0.1', 'djangoapp', 'Ad09faf134D')
    or die('Could not connect: ' . mysql_error());
mysql_select_db('djangoapp', $link)or die('Could not select database');

function microtime_used($before,$after) {
    return (substr($after,11)-substr($before,11))
        +(substr($after,0,9)-substr($before,0,9));
}
function timeit($cmd, $iterations)
{
    global $memcached, $key_list, $key_list_miss;
    $s = microtime();
    for ($n=1; $n<=$iterations; $n++)
    {
        eval($cmd);
    }
    $f = microtime();
    return 1000.0*microtime_used($s, $f)/$iterations;
}

$hosts = array('127.0.0.1:11211');
$memcache = new Memcache;
$memcache->connect('localhost', 11211) or die ("Could not connect");

$key_list = array();
$key_list_miss = array();
for ($i=1; $i<=100; $i++)
{
    $key_list[] = 'hit'.$i;
    $key_list_miss[] = 'miss'.$i;
}
$results = mysql_query('SELECT * FROM articles_article LIMIT 0,100') or die('Query failed: ' . mysql_error());
foreach ($key_list as &$value)
{
    $memcached->set($value, mysql_fetch_array($results));
}

if (count($argv) > 1)
{
    $n = $argv[1];
}
else
{
    $n = 1000;
}

echo "performing ".$n." iterations\n";
echo "### DB QUERY ###\n";
$t = timeit('mysql_query("SELECT * FROM articles_article LIMIT 0,1") or die("sql error");', $n);
printf("%.3f ms/pass\n", $t);
flush();
echo "### CACHE HITS ###\n";
echo "single call; hit\n";
$t = timeit('$memcached->get($key_list[0]);', $n);
printf("%.3f ms/pass\n", $t);
flush();
echo "multi(5) call; hit\n";
$t = timeit('$memcached->get(array_slice($key_list, 0, 5));', $n);
printf("%.3f ms/pass\n", $t);
flush();
echo "multi(10) call; hit\n";
$t = timeit('$memcached->get(array_slice($key_list, 0, 10));', $n);
printf("%.3f ms/pass\n", $t);
flush();
echo "single call; miss\n";
$t = timeit('$memcached->get($key_list_miss[0]);', $n);
printf("%.3f ms/pass\n", $t);
flush();
echo "multi(5) call; miss\n";
$t = timeit('$memcached->get(array_slice($key_list_miss, 0, 5));', $n);
printf("%.3f ms/pass\n", $t);
flush();
echo "multi(10) call; miss\n";
$t = timeit('$memcached->get(array_slice($key_list_miss, 0, 10));', $n);
printf("%.3f ms/pass\n", $t);
flush();
?>
