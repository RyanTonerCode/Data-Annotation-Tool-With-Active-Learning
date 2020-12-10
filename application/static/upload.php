<?php

if(isset($_FILES['file']['name'])){

   $filename = $_FILES['file']['name'];

   $location = "upload/".$filename;
   $DatasetFileType = pathinfo($location,PATHINFO_EXTENSION);
   $DatasetFileType = strtolower($DatasetFileType);

   $valid_extensions = array("csv","json","txt");

   $response = 0;
   if(in_array(strtolower($DatasetFileType), $valid_extensions)) {
      if(move_uploaded_file($_FILES['file']['tmp_name'],$location)){
         $response = $location;
      }
   }

   echo $response;
   exit;
}

echo 0;