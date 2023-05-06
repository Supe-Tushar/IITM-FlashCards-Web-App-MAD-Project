var lastReviewed = true;
var lastReviewedRowId = document.getElementById('lastReviewedRowId').innerHTML;
console.log(lastReviewedRowId);

if (lastReviewed) {
    highlightLastReviewedRow();
}

function highlightLastReviewedRow() {
    var z = document.getElementById("all_decks");
    if(z != null) {
        z = z.rows[lastReviewedRowId].getElementsByTagName('td');
        console.log(z);
        for (let i = 0; i < z.length; i++) {
          z[i].style.backgroundColor = "#83ef4e";
        }
    }
}