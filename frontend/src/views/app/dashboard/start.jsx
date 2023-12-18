import React, {useEffect} from 'react';
import { Row } from 'reactstrap';
import { Colxx, Separator } from '../../../components/common/CustomBootstrap';
import Breadcrumb from '../../../containers/navs/Breadcrumb';
import { Card, CardBody, CardTitle, CardHeader } from 'reactstrap';
import { CircularProgressbar } from 'react-circular-progressbar';
import IconCard from '../../../components/cards/IconCard';
import GradientWithRadialProgressCard from '../../../components/cards/GradientWithRadialProgressCard';



const Start = ({ match }) => {
  const [diagnosticData, setDiagnosticData] = React.useState({
    cache_size: 35414,
    database: {
      size: 500,
      query_time: 12,
    },
    disk: {
      total: 1000,
      used: 250,
      free: 750
    }
  });
  const [loading, setLoading] = React.useState(true);

  useEffect(() => {
    setDiagnosticData(diagnosticData) // replace with request
    setLoading(false)
  }, []);

  if (loading){
    return <div className="loading"></div>

  }
  return (
    <>
      <Row>
        <Colxx xxs="12">
          <Breadcrumb heading="dashboard" match={match} />
          <Separator className="mb-5" />
        </Colxx>
      </Row>
      <Row>
        <Colxx xxs="12" className="">
          <Row className="icon-cards-row mb-2">
            <Colxx xxs="6" sm="4" md="3" lg="2">
              <IconCard {...{ title: 'Cache Size', icon: "iconsminds-arrow-refresh", value: `${Math.round(diagnosticData?.cache_size/1000/1000)} MB` }} className="mb-4 w-100" />
            </Colxx>
            <Colxx xxs="6" sm="4" md="3" lg="2">
              <IconCard {...{ title: 'Database Size', icon: "iconsminds-arrow-refresh", value: `${diagnosticData?.database?.size} MB` }} className="mb-4 w-100" />
            </Colxx>
            <Colxx xxs="6" sm="4" md="3" lg="2">
              <IconCard {...{ title: 'Database Query Time', icon: "iconsminds-arrow-refresh", value: `${Math.round(diagnosticData?.database?.query_time * 1000)} MS` }} className="mb-4 w-100" />
            </Colxx>
            <Colxx xxs="6" sm="4" md="3" lg="2">
              <IconCard {...{ title: 'Storage Total', icon: "iconsminds-arrow-refresh", value: `${diagnosticData?.disk?.total} GB`}} className="mb-4 w-100" />
            </Colxx>
            <Colxx xxs="6" sm="4" md="3" lg="2">
              <IconCard {...{ title: 'Storage Used', icon: "iconsminds-arrow-refresh", value: `${diagnosticData?.disk?.used} GB`}} className="mb-4 w-100" />
            </Colxx>
            <Colxx xxs="6" sm="4" md="3" lg="2">
              <IconCard {...{ title: 'Storage Free', icon: "iconsminds-arrow-refresh", value: `${diagnosticData?.disk?.free} GB`}} className="mb-4 w-100" />
            </Colxx>
          </Row>
        </Colxx>
      </Row>

    </>
  )
};
export default Start;
