<?php
	//Liste der Elemente, die benötigt werden: o -> Optional, r -> Required, d -> Don't pass into 'in'
	//TODO ADD DB Select of these Fields!
	$list = array(
			  'authHash' => 'rd'
			, 'Password' => 'rd'
			
			);
	$raw = $_POST;
	$in = allSet($_POST,$list);
	$in['Errors'] = "";
	$dir = dirname( __FILE__ );
	include_once(substr($dir,0,-19)."/dbcon.php");
	header('Content-Type: application/json; charset=utf-8');	
	if($dbcon->isConnected()){
		if($in['complete'] === 'true'){
			$id = $dbcon->login($in['authHash'],$in['Password']);
			if(isset($id['id'])){
				//TODO Hier weiter auf PDO umstellen
				$in['id'] = $id['id'];
				
			}else{
				$in['Errors'] .= $id;
			}
			
		}else{
			if(isset($raw['authRequired']) && $raw['authRequired'] == 'true' && isset($raw['mac']) && $raw['authRequired'] != ""){
				$in = $dbcon->createCredentials($raw['mac']);
				
			}else{
				$in['Errors'] = 'AuthRequired! Check Credentials';
			}
		}
	}else{
		
	}
	header('Content-Type: application/json; charset=utf-8');
	echo json_encode($in,JSON_PRETTY_PRINT);
	
	
	function allSet($array,$check){
		$filled = array();
		$filled['in'] = array();
		$filled['complete'] = 'true';
		foreach($check as $field => $value){
			if(isset($array[$field])){
				if(strpos($value,'d') !==false){
					$filled[$field]=$array[$field];
				}else{
					$filled['in'][$field]=$array[$field];
				}
				
			}else{
				//Check if field was requiered;
				if(strpos($value,'r') !==false){
					$filled['in'][$field]='';
					$filled['complete'] = 'false';
				}elseif(strpos($value,'o') !==false){
					$filled['in'][$field]='';
				}
			}
		}
		return $filled;
	}
?>