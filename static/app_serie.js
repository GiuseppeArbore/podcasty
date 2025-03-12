'use strict;'

document.querySelector("#showallep").addEventListener('click' , e => {
    e.preventDefault();
    const episodi = document.querySelectorAll('.myep');
    const btn= document.querySelector('.myall');
    btn.classList.add('hide');
    for (let episod of episodi){
      episod.classList.remove('hide');
    }
});

document.querySelector("#searchep").addEventListener('click' , e => {
  e.preventDefault();
  let filtro=document.getElementById("search_in").value;
  const btn= document.querySelector('.myall');
  btn.classList.remove('hide');
  const episodi = document.querySelectorAll('.myep');
    for (let episod of episodi){
      let title = episod.dataset.tit;
      const descrizione = episod.dataset.descr;
      episod.classList.add('hide');
      if ( title.includes(filtro) || descrizione.includes(filtro) )
        episod.classList.remove('hide');
    }
});
