import React from 'react';
import { useState, useEffect } from 'react';

import { Row } from 'reactstrap';
import { Badge } from 'reactstrap';
import { useHistory } from 'react-router-dom/cjs/react-router-dom.min';

import Pagination from './Pagination';
import ContextMenuContainer from './ContextMenuContainer';
import DataListView from './DataListView';
import ImageListView from './ImageListView';
import ThumbListView from './ThumbListView';

function collect(props) {
  return { data: props.data };
}

const ListPageListing = ({
  items,
  selectedItems,
  onCheckItem,

}) => {
  const [selectedFilms, setSelectedFilms] = useState([]);

  const select = (filmUUID) => {
    if (selectedFilms.includes(filmUUID)) {
      setSelectedFilms(selectedFilms.filter((uuid) => uuid !== filmUUID));
      return
    }
    setSelectedFilms([...selectedFilms, filmUUID]);
  }

  const history = useHistory();

  const send = () => {
    // does the sendo
    fetch("/api/queue_add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(selectedFilms)
    })
      .then(resp => {
        if (resp.status !== 200) {
          document.getElementById('fCountIndicator').textContent = "Error"
        }else{
          document.getElementById('fCountIndicator').textContent = "Sent... Redirecting..."
          setTimeout(() => {
            history.push('/foutre/films')
          }, 2000)
        }
      })
  }

  return (
    <Row className=''>
      {items.map((film) => {
        return (
          <ImageListView
            key={film.id}
            film={film}
            isSelect={selectedFilms.includes(film.uuid)}
            selectFunc={select}

          />
        );
      })}
      {!!selectedFilms.length && <Badge className='fCountIndicator' color='primary' id='fCountIndicator' onClick={send}>{selectedFilms.length} Films Selected</Badge>}
    </Row>
  );
};

export default React.memo(ListPageListing);
