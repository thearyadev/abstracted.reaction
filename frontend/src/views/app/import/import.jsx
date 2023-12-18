import React, {useEffect} from 'react';
import { Row } from 'reactstrap';
import { Colxx, Separator } from '../../../components/common/CustomBootstrap';
import Breadcrumb from '../../../containers/navs/Breadcrumb';
import IconCard from '../../../components/cards/IconCard';



const Import = ({ match }) => {

  return (
      <>
        <Row>
          <Colxx xxs="12">
            <Breadcrumb heading="import" match={match} />
            <Separator className="mb-5" />
          </Colxx>
        </Row>
        <Row>
          <Colxx xxs="12" className="">
            <h1>:3</h1>
          </Colxx>
        </Row>

      </>
  )
}

export default Import