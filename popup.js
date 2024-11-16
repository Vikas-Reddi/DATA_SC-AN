document.addEventListener('DOMContentLoaded', function() {
  document.body.style.overflow = 'hidden';
  document.documentElement.style.overflow = 'hidden';
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      const currentUrl = tabs[0].url;
      const title = tabs[0].title;
      
      const urlTitle = document.getElementById('title');
    
      urlTitle.textContent = title;
  
      // Call the async function to extract data and update the text
      // Extract status after extracting data (corrected order)
      extract_data(currentUrl).then((text) => {
        extract_summ(text).then((summ)=>{
          extract_sta(text,currentUrl).then((stat) => {
            let stat1 = "loading"
            const status = document.getElementById('status'); // Corrected element ID
            status.textContent = stat;
            stat1 = stat;
            document.querySelectorAll('.loading').forEach(function(element) {
              element.src = stat+".png";
          });
          document.querySelectorAll('.cms').forEach(function(element) {
            element.src ="icon2_"+ stat+".png";
        });
            document.querySelectorAll('*').forEach(function(element) {
              // Check if the class contains 'loading'
              element.classList.forEach(function(className) {
                  if (className.includes('loading')) {
                      // Replace 'loading' with 'real' (or any other string you want)
                      element.classList.replace(className, className.replace('loading', stat));
                  }
              });
          
          });
          
          }).catch((error) => {
            console.error('Error:', error);
            // Update the text element with an error message if needed
            const status = document.getElementById('status'); // Corrected element ID
            status.textContent = 'Error: Has Occered '; // Provide a more informative error message
          });
          const summarised = document.getElementById("text_s");
         
          summarised.textContent = summ;
        }).catch((error) => {
          console.error('Error:', error);
          // Update the text element with an error message if needed
          const summarised = document.getElementById("text_s");
          summarised.textContent = 'Error: Has Occered '; 
        
      }).catch((error) => {
        console.error('Error:', error);
      });
    });
  });});

async function extract_data(url) {
  const requestBody = {
    url: url
  };

  try {
    const response = await fetch('https://ser-vikas9870s-projects.vercel.app/extract', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    // Check if the response is OK
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get the text response from the server
    const responseText = await response.text();
    return responseText; // Return the extracted text
    
  } catch (error) {
    console.error('Error:', error);
    return 'ERROR'; // Return 'ERROR' if an issue occurs
  }
}
async function extract_sta(text,currentUrl){
    const requestBody = {
        text: text
      };
      try {
        const response = await fetch('https://dep-lmkf.onrender.com/predict', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });
    
        // Check if the response is OK
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        let responseText = await response.json();
        let stat = responseText.prediction;
        
    return stat;
} catch (error) {
    console.error('Error:', error);
    return 'ERROR'; // Return 'ERROR' if an issue occurs
  }
}
async function extract_summ(text){
  const requestBody = {
      text: text,
      num_sentences: 3
    };
    try {
      const response = await fetch('https://summ.onrender.com/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
  
      // Check if the response is OK
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const responseText = await response.json();
      
       
      
  return responseText.summary;
} catch (error) {
  console.error('Error:', error);
  return 'ERROR'; // Return 'ERROR' if an issue occurs
}
}