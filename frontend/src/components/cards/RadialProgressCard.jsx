import React from 'react';
import { Card, CardBody, CardTitle, CardHeader } from 'reactstrap';
import { CircularProgressbar } from 'react-circular-progressbar';

const RadialProgressCard = ({
  title = 'title',
  percent = 50,
  isSortable = false,
}) => {
  return (
    <Card style={{boxShadow: "none"}} className='p-0'>
      {isSortable && (
        <CardHeader className="p-0 position-relative">
          <div className="position-absolute handle card-icon">
            <i className="simple-icon-shuffle" />
          </div>
        </CardHeader>
      )}
      <CardBody className="d-flex justify-content-between align-items-center p-2">
        <CardTitle className="mb-0">{title}</CardTitle>
        <div className="progress-bar-circle">
          <CircularProgressbar
            strokeWidth={4}
            value={percent * 10}
            text={`${percent}`}
          />
        </div>
      </CardBody>
    </Card>
  );
};
export default React.memo(RadialProgressCard);
