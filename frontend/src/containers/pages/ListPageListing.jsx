import React from 'react';
import { useState } from 'react';
import { Row } from 'reactstrap';
import ImageListView from './ImageListView';

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
  return (
    <Row className=''>
      {items.map((film) => {
        return (
          <ImageListView
            key={film.uuid}
            film={film}
            isSelect={selectedFilms.includes(film.uuid)}
            selectFunc={select}

          />
        );
      })}
    </Row>
  );
};

export default React.memo(ListPageListing);
