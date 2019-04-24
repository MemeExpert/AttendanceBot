const app = document.getElementById('root')


const container = document.createElement('div')
container.setAttribute('class', 'container')

//app.appendChild(logo)
app.appendChild(container)
var searchType=0; //0=username , 1=eventname
function createEvent() {
  console.log("event creating")
  theRest();
}

function theRest(){


  console.log(url+"?"+params)

}
