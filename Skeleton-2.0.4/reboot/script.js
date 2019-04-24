const app = document.getElementById('root')

const logo = document.createElement('img')
logo.src = 'logo.png'

const container = document.createElement('div')
container.setAttribute('class', 'container')

//app.appendChild(logo)
app.appendChild(container)
var searchType=0; //0=username , 1=eventname
function searchName() {
  searchType = 0
  console.log("username")
  theRest();
}
function searchEvent() {
  searchType = 1
  console.log("event name")
  theRest();
}


function theRest(){

  console.log("searchtype" +searchType)
  var url;
  var params;
  var name;
  if(searchType===0){
    url = "http://127.0.0.1:5000/api/signup"
    name=prompt("Please enter user name to search","name")
    params = "userDisplayName="+name
  }
  if(searchType===1){
    url = "http://127.0.0.1:5000/api/event"
    name=prompt("Please enter event name to search","name")
    params = "title="+name
  }

  console.log(url+"?"+params)
  var request = new XMLHttpRequest()
  request.open('GET', url+"?"+params, true)
  request.onload = function() {
    // Begin accessing JSON data here
    var data = JSON.parse(this.response)
    if (request.status >= 200 && request.status < 400) {
      var lel=document.getElementsByClassName("card")

      if(searchType===0){
        for(var x=0 ; x<data["data"][0].length ; x++){
          console.log("event title: " + data["data"][0][x]["event"]["title"])

      //   var card=document.getElementById('results')


          const card = document.createElement('div')
          card.setAttribute('class','card')

          const h1 = document.createElement('h1')
          h1.textContent = data["data"][0][x]["event"]["title"]

          const p = document.createElement('p')
          var lel = data["data"][0][x]["event"]["occurence_date"].substring(0,10)+ "     "+data["data"][0][x]["event"]["occurence_date"].substring(11, 19)
          p.textContent = "Event Date:\t "+lel+"\n"
          p.textContent+= "Event Host:\t \t "+ data["data"][0][x]["event"]["creator"]["displayName"]+"\n"
          p.textContent+= "Attendee:\t \t "+ name

          card.style.display = "inline";


          container.appendChild(card)
          card.appendChild(h1)
          card.appendChild(p)
        }
      }else{
        for(var x=0 ; x<data["data"][0].length ; x++){
          console.log("event title: " + data["data"][0][x]["title"])

          const card = document.createElement('div')
          card.setAttribute('class','card')

          const h1 = document.createElement('h1')
          h1.textContent = data["data"][0][x]["title"]

          const p = document.createElement('p')
          var lel = data["data"][0][x]["occurence_date"].substring(0,10)+ "     "+data["data"][0][x]["occurence_date"].substring(11, 19)
          p.textContent = "Event Date:\t "+lel+"\n"
          p.textContent+= "Event Host:\t \t "+ data["data"][0][x]["creator"]["displayName"]
          container.appendChild(card)
          card.appendChild(h1)
          card.appendChild(p)
        }
      }
  //    var butt = document.createElement("BUTTON");
    //  var buttTxt = document.createTextNode("Clear results")
      //x.appendChild(t)













  /*    for (var key in data){
        if (data.hasOwnProperty(key)){

          console.log(key + " -> " +data[key]);
          console.log(searchType)
          if(searchType===0){
            eventSearch => {
              const card = document.createElement('div')
              card.setAttribute('class', 'card')

              const h1 = document.createElement('h1')
              h1.textContent = eventSearch.event.title

              const p = document.createElement('p')
              eventSearch.event.occurence_date = eventSearch.event.occurence_date.substring(0, 16)
              p.textContent = "Event Creator: "+ eventSearch.event.creator.displayName +"\n"
              p.textContent+= "Date: "+ eventSearch.event.occurence_date

              container.appendChild(card)
              card.appendChild(h1)
              card.appendChild(p)
            }

          }else{
            const card = document.createElement('div')
            card.setAttribute('class', 'card')

            const h1 = document.createElement('h1')
            h1.textContent = data[key].title

            const p = document.createElement('p')
            data[key].event.occurence_date = data[key].event.occurence_date.substring(0, 16)
            p.textContent = "Event Creator: "+ data[key].creator.displayName +"\n"
            p.textContent+= "Date: "+ data[key].occurence_date

            container.appendChild(card)
            card.appendChild(h1)
            card.appendChild(p)
/*
          eventSearch => {
              const card = document.createElement('div')
              card.setAttribute('class', 'card')

              const h1 = document.createElement('h1')
              h1.textContent = eventSearch.title

              const p = document.createElement('p')
              eventSearch.occurence_date = eventSearch.occurence_date.substring(0, 16)
              p.textContent = "Event Creator: "+ eventSearch.creator.displayName +"\n"
              p.textContent+= "Date: "+ eventSearch.occurence_date

              container.appendChild(card)
              card.appendChild(h1)
              card.appendChild(p)
            }
          }
        }
      }*/

    } else {
      const errorMessage = document.createElement('marquee')
      errorMessage.textContent = `Gah, it's not working!`
      app.appendChild(errorMessage)
    }
  }

  request.send()
}
