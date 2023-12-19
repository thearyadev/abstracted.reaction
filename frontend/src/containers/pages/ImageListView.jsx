import React from 'react';
import {
  Row,
  Card,
  CardBody,
  CardSubtitle,
  CardImg,
  CardText,
  CustomInput,
  Badge,
  CardHeader,
} from 'reactstrap';
import { NavLink } from 'react-router-dom';
import classnames from 'classnames';
import { ContextMenuTrigger } from 'react-contextmenu';
import { Colxx } from '../../components/common/CustomBootstrap';
import LazyLoad from 'react-lazyload';
import { useLocation } from 'react-router-dom/cjs/react-router-dom.min';
import { Container } from 'reactstrap';

const ImageListView = ({ film, isSelect, selectFunc }) => {
  const location = useLocation();
  const currentPathname = location.pathname;

    return (
      <Colxx sm="6" lg="4" xl="3" className="mb-3" key={film.uuid}>
        <Card
          onClick={(event) => { }}
          className='video-listing-card'
        >
          <NavLink to={`${currentPathname}/${film.uuid}`} className="">

            <div className="position-relative">
              <LazyLoad height={200} offset={1200} throttle={100}>


                <CardImg top alt={film.title} src={import.meta.env.DEV ? `/assets/img/films/${film.uuid}.png` : `/api/thumbnail?uuid=${film.uuid}`} />

              </LazyLoad>
              <Badge
                color={film.state === 'COMPLETE' ? (film.watched === true ? "success" : "danger") : (film.state === 'DOWNLOADING' ? "warning" : "secondary")}
                pill
                className="position-absolute badge-top-left info-pill"
              >
                {/* if complete                     use watch status                             else: use film state */}
                {film.state === 'COMPLETE' ? (film.watched === true ? "WATCHED" : "UNWATCHED") : (film.state === "DOWNLOADING" ? `DOWNLOADING: ${film.download_progress}%` : film.state)}
              </Badge>
            </div>
            <CardBody className="p-3 pb-0">
              <Row>
                <Colxx xxs="12" className="mb-3">
                  <CardText className="text-muted text-small mb-0 font-weight-light text-truncate">{film.actresses.join(", ")}</CardText>
                  <CardSubtitle className="font-weight-bold pt-3 text-truncate">{film.title}</CardSubtitle>
                  <div className='d-flex justify-content-between'>
                    <CardText className="text-muted text-small mb-0 mt-0 pt-0 font-weight-light">
                      {film.date_added}
                    </CardText>
                    <div className="d-flex align-items-center">
                      <span className="font-weight-bold mr-2">{film.rating.average !== 0 ? film.rating.average : '-'}</span>
                      {film.rating.average !== 0 ? <span className='simple-icon-star' /> : null}
                    </div>
                  </div>
                </Colxx>
              </Row>
            </CardBody>
          </NavLink>

        </Card>
      </Colxx>
    );


};

/* React.memo detail : https://reactjs.org/docs/react-api.html#reactpurecomponent  */
export default React.memo(ImageListView);
