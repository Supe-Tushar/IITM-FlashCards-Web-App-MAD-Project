function flipcard() {
  var x = document.getElementById("word");
  var y = document.getElementById("answer");
  if (y.style.display === "none"){
    x.style.display = "none"; //show answer
    y.style.display = "block"; //hide word
  }
  else{
    y.style.display = "none";
    x.style.display = "block";
  }
}
