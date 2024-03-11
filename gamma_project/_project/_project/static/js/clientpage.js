const rightconexpend = document.getElementById('rightconexpend')
const rightcon = document.querySelector('.rightcon')
const leftcon = document.getElementById('leftcon');
leftcon.onscroll  = ()=>{
    clientcon.style.top="0"
    bottomclientCon.style.bottom="0"
}
//-----------------------------------------------------------------------------------------------------------
//right container menu size funcion 
rightconexpend.addEventListener('click',()=>{
    rightcon.classList.toggle( "active" );
})
//-----------------------------------------------------------------------------------------------------------
const currentDate = new Date();
const month = currentDate.getMonth() + 1;
const day = currentDate.getDate();
const year = currentDate.getFullYear();
// Format the date as a string=====================================================================
const formattedDate = `${month}/${day}/${year}`;
const billDate = document.querySelectorAll('#billDate')
billDate.forEach((bd)=>{
bd.innerHTML=formattedDate
})
const sellsdel = document.querySelectorAll('#sellsdel')
const windowcon = document.getElementById('windowcon')
const closedetwin = document.getElementById('closedetwin')
const clientcon = document.getElementById('clientcon')
const bottomclientCon = document.getElementById('bottomclientCon')
sellsdel.forEach((sellsdel)=>{
sellsdel.onclick=()=>{
    const metadata = sellsdel.getAttribute('metadata')
    windowcon.style.visibility = 'visible'
    windowcon.style.opacity = '1'
    document.getElementById('detailcontainer').innerHTML=metadata
    
}
})
closedetwin.addEventListener('click',()=>{
windowcon.style.top='0'
windowcon.style.visibility='hidden'
windowcon.style.opacity='0'
})
// sorting the table
document.addEventListener("DOMContentLoaded", function () {
var sellstable = document.querySelector(".sellstable");
var tbody = sellstable.querySelector("tbody");
var rows = Array.from(tbody.querySelectorAll("tr"));
rows.sort(function (a, b) {
var dateA = new Date(a.cells[1].textContent);
var dateB = new Date(b.cells[1].textContent);
return dateB - dateA; 
});
tbody.innerHTML = "";
rows.forEach(function (row) {
tbody.appendChild(row);
});
});
//print all table functions =======================================================================
const printAll =  document.querySelectorAll('#printall')
printAll.forEach((btn)=>{
btn.onclick=function(){
// document.querySelectorAll('editdept').style.display='none';
document.getElementById('printallcon').style.display='flex';
document.getElementById('tableprintallbody').innerHTML=document.getElementById('tablebody').innerHTML
// Get a reference to the table with the ID "tableprintbody"
const tabled=document.getElementById('tableprintallbody')
const rows = tabled.rows
const totalrows = tabled.querySelectorAll("tr.subtotal");
totalrows.forEach((row) => {
row.style.display = "none";
});

const paidrows = tabled.querySelectorAll("tr.paied");
paidrows.forEach((row) => {
row.style.display = "none";
})
// Loop through each row in the table
console.log(rows)
for (let i = rows.length - 1; i >= 0; i--) {
    const row = rows[i];
      // Delete cells at indices 1, 2, 3, and 4 in descending order to maintain correct indices
    for (let k = -1; k < 0; k++) {
        row.deleteCell(k);
    }
}
}})
document.getElementById('closeprintallcon').addEventListener('click',function(){
document.getElementById('printallcon').style.display='none'
})
document.getElementById('printallbtn').addEventListener('click', function(){
printDiv('printallcontent')    
})
// priont selected parts by checkboxes functions ================================================================
// const printCelect =document.querySelectorAll('#print') 
// printCelect.forEach((btn)=>{
// btn.addEventListener('click',function(){
// const checkboxes = document.querySelectorAll('input[type="checkbox"]');
// const selectedTable = document.getElementById('tableprintbody');
// selectedTable.innerHTML='';
// checkboxes.forEach(checkbox=>{
//     if(checkbox.checked){
//         document.getElementById('printcon').style.display='flex';
//         const rows = checkbox.parentNode.parentNode.cloneNode(true);
//         rows.deleteCell(0)
//         rows.deleteCell(-1)
//         rows.deleteCell(-1)
//         rows.deleteCell(-1)
//         rows.deleteCell(-1)
//         selectedTable.appendChild(rows)
//     }else{
//         document.getElementById('selectdatecon').style.display='flex';
//     }
// })
// })})
// document.getElementById('closeprintcon').addEventListener('click',function(){
// document.getElementById('printcon').style.display='none'
// const selectedTable = document.getElementById('tableprintbody');
// selectedTable.innerHTML='';
// })
// document.getElementById('closeseldatecon').addEventListener('click',function(){
// document.getElementById('selectdatecon').style.display='none'
// })
// document.getElementById('printbtn').addEventListener('click', function(){
// printDiv('printcontent')    
// })
//print by date function ==================================================================
// const originalTable = document.getElementById("tablebody");
// const newTable = document.createElement("table");
// const startDateInput = document.getElementById("startDate");
// const endDateInput = document.getElementById("endDate");

// function filterAndShowRows() {
// const startDate = new Date(startDateInput.value);
// const endDate = new Date(endDateInput.value);
// const rowsArray =originalTable.getElementsByTagName('tr');
// var tableprintbody =document.getElementById('tableprintbody');
// for(i=1; i<rowsArray.length;i++){
//     const filteredRows = [];
//     const dateString =rowsArray[i].getElementsByTagName("td")[2].textContent;
//     const date = new Date(dateString);
//     if (date >= startDate && date <= endDate) {
//         filteredRows.push(rowsArray[i]);
//     }
//         for(k=0;k<filteredRows.length;k++){
//             const clonedRow = filteredRows[k].cloneNode(true); 
//             newTable.appendChild(clonedRow); 
//         } 
//         const totalrows = newTable.querySelectorAll("tr.subtotal");
//         totalrows.forEach((row) => {
//         row.style.display = "none";
//         });
    
//         const paidrows = newTable.querySelectorAll("tr.paied");
//         paidrows.forEach((row) => {
//         row.style.display = "none";
//         })
//         tableprintbody.innerHTML = newTable.innerHTML;
//     }
//     prows = tableprintbody.querySelectorAll("tr.salesrow");
//     prows.forEach((row)=>{
//         row.deleteCell(0)
//         row.deleteCell(-1)
//         row.deleteCell(-1)
//         row.deleteCell(-1)
//         row.deleteCell(-1)
//     })
//     newTable.innerHTML = "";
// }

// document.getElementById("filterButton").addEventListener("click", ()=>{
//     document.getElementById('selectdatecon').style.display='none';
//     document.getElementById('printcon').style.display='flex';
//     filterAndShowRows();
// });
// print paper function =======================================================================
function printDiv(divId) {
var divToPrint = document.getElementById(divId);
var newWin = window.open('', '_blank');
newWin.document.open();
newWin.document.write(`<html><head><title>Print</title>
<link rel="stylesheet" href="{% static "css/main.css" %}">
<style>
*{
padding: 0;
margin: 0;
box-sizing: border-box;
font-family: Arial, Helvetica, sans-serif;
}
body{direction:ltr;display:flex; align-items:start; flex-direction:column;height:100vh; background:#fff;}
#printcontent table,#printallcontent table{
width: 90%;
text-align: center;
border-radius: 10px;
overflow: hidden;
border: 1px solid #040404;
}
#printcontent table thead,#printallcontent table thead{
background-color:#74C785;
}
#printcontent table th,#printallcontent table th{
font-size: 20px;
color: #000;
padding: 5px;
border-bottom: 1px solid #625D5D;
}
#printcontent table td,#printallcontent table td{
font-size: 20px;
border: 1px solid #625D5D;
padding: 5px;
color: #040404;
}
#printcontent table td .btn,#printallcontent table td .btn{
border: none;
background-color: transparent;
font-size: 20px;
cursor: pointer;
}
#printcontent,#printallcontent{
width:100%;
top: 10%;
display: flex;
align-items: center;
justify-content: center;
flex-direction: column;
direction: ltr;
}
#printcontent .detcon,#printallcontent .detcon{
margin: 5px;
width: 80%;
display: flex;
justify-content: space-around;
align-items: start;
flex-wrap: wrap;
flex-direction: row;
}
#printcontent .detcon div,#printallcontent .detcon div{width: 40%; text-align: center;}
#printcontent .detcon table,.detcon ul,#printallcontent .detcon table{
width: 90%;
text-align: center;
}
#printcontent img,#printallcontent img{
width: 40%;
}
#printcontent h2,#printallcontent h2{
margin: 10px;
font-size:25px;
}
#printcontent ul,#printallcontent ul{
width: 80%;
list-style: none;
background-color: #fff;
border-radius: 10px;
overflow: hidden;
}
#printcontent ul .head,#printallcontent ul .head{
background-color:#74C785;
color: #000;
}
#printcontent ul li,#printallcontent ul li{
padding: 5px ;
font-size: 25px;
color: #040404;
font-weight: 600;
border-bottom: 1px solid #625D5D;
text-align: center;
}
</style>
</head><body>`);
newWin.document.write(divToPrint.outerHTML);
newWin.document.write('</body></html>');
newWin.document.close();
newWin.print();
newWin.close();
window.location.href="{% url 'clientpage' client.id %}"
}
//payment window functions ===============================================================
let addpay = document.querySelectorAll('#addpay')
let profitcon = document.getElementById('profitcon')
let closeprofit = document.getElementById('closeprofit')
addpay.forEach((btn)=>{
btn.onclick=()=>{
profitcon.style.display='flex'
document.getElementById('moneypay').focus();
}})
