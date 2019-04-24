const button = document.getElementById('post-btn');
button.addEventListener('click', async _ => {
  try {
    var tit=prompt("Enter event title", "Weekly Lunch")
    var date="2019-05-01T22:00:00+00:00"
    var creator_id=74294738
    const response = await fetch('http://127.0.0.1:5000/api/event', {
      method: 'post',
      body: {
        "title":tit,
        "occurence_date":date,
        "creator_id":creator_id
      }
    });
    console.log('Completed!', response);
  } catch(err) {
    console.error(`Error: ${err}`);
  }
});
