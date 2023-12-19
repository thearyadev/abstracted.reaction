import React, {useContext} from 'react';
import { Row } from 'reactstrap';
import { Colxx, Separator } from '../../../components/common/CustomBootstrap';
import Breadcrumb from '../../../containers/navs/Breadcrumb';
import { ActressTable } from '../../../containers/ui/ReactTableCards';
import {ActressesContext} from "../../../providers/actressesProvider.jsx";

const Actress_list = ({ match }) => {
    const actresses = useContext(ActressesContext).map(actress => {return {name: actress}})
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
                <ActressTable data={actresses} />
            </Colxx>
          </Row>
        </>
      )
};
export default Actress_list;
