'use strict;'

document.querySelector("#search_s").addEventListener('click' , e => {
  e.preventDefault();
  let filtro=document.getElementById("cerca_in").value;
  const btn= document.querySelector('.myall');
  btn.classList.remove('hide');
  const serie = document.querySelectorAll('article');
    for (let s of serie){
      let categ = s.dataset.categ;
      s.classList.add('hide');
      if ( categ.includes(filtro))
        s.classList.remove('hide');
    }
});


document.querySelectorAll('div > main > article > div > div > #catjs').forEach(link => {
  link.addEventListener('click', e => {             //al click del mouse su a:   in e.target ho l'elemento che ho cliccato
    e.preventDefault(); 
    const filter = e.target.dataset.filcat;
    const btn= document.querySelector('.myall');
    btn.classList.remove('hide');
    const articles = document.querySelectorAll('article');
    for (let article of articles){
      const category = article.dataset.categ;
      article.classList.add('hide');
      if (filter == category)
        article.classList.remove('hide');
    }
  });
});

document.querySelector("#showall").addEventListener('click' , e => {
  e.preventDefault();
  const articles = document.querySelectorAll('article');
  const btn= document.querySelector('.myall');
  btn.classList.add('hide');
  for (let article of articles){
    article.classList.remove('hide')
  }
});

