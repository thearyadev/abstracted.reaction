import React from 'react';
import { Row } from 'reactstrap';
import { Colxx, Separator } from '../../../components/common/CustomBootstrap';
import Breadcrumb from '../../../containers/navs/Breadcrumb';
import { ActressTable } from '../../../containers/ui/ReactTableCards';
import { useSelector } from 'react-redux';


const Start = ({ match }) => {
  const actressesData = useSelector(state => state.actresses.actresses);

  return (
    <>
      <Row>
        <Colxx xxs="12">
          <Breadcrumb heading="actresses" match={match} />
          <Separator className="mb-5" />
        </Colxx>
      </Row>
      <Row>
        <Colxx xxs="12" className="mb-4">
          <ActressTable data={actressesData} />
        </Colxx>
      </Row>
    </>
  )
};
export default Start;
