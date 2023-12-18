import { Row, Col } from 'reactstrap';
import IntlMessages from '../../../helpers/IntlMessages';
import { Colxx, Separator } from '../../../components/common/CustomBootstrap';
import Breadcrumb from '../../../containers/navs/Breadcrumb';
import ListPageListing from '../../../containers/pages/ListPageListing';
import { DropdownToggle, DropdownItem, DropdownMenu, ButtonDropdown } from 'reactstrap';
import { useState,  } from 'react';
import { useSelector,  } from 'react-redux';

const sortingOptions = [
  { value: "DANF", label: "Date Added (Newest First)" },
  { value: "DAOF", label: "Date Added (Oldest First)" },
  { value: "UW", label: "Unwatched" },
  { value: "W", label: "Watched" },
  { value: "RLTH", label: "Rating (Low to High)" },
  { value: "RHTL", label: "Rating (High to Low)" },
  { value: "DL", label: "Downloading" }
]

function sortFilms(filmArray) {
  const sortingMethod = localStorage.getItem("sorting_method");
  switch (sortingMethod) {
    case "DAOF":
      return filmArray.sort((a, b) => new Date(a.date_added) - new Date(b.date_added))
    case "UW":
      return filmArray.filter(item => item.watched !== true && item.state === 'COMPLETE').sort((a, b) => new Date(b.date_added) - new Date(a.date_added))
    case "W":
      return filmArray.filter(item => item.watched === true && item.state === 'COMPLETE').sort((a, b) => new Date(b.date_added) - new Date(a.date_added))
    case "RHTL":
      return filmArray.filter(item => item.watched !== false && item.state === 'COMPLETE').sort((a, b) => b.average - a.average)
    case "RLTH":
      return filmArray.filter(item => item.watched !== false && item.state === 'COMPLETE').sort((a, b) => a.average - b.average)
    case "DL":
      return filmArray.filter(item => item.state !== 'COMPLETE').sort((a, b) => new Date(b.date_added) - new Date(a.date_added))
    default:
      return filmArray.sort((a, b) => new Date(b.date_added) - new Date(a.date_added))
  }
}

function setSortingMethod(method) {
  localStorage.setItem("sorting_method", method)

}

const Start = ({ match }) => {
  const [sortingDropdownOpen, setSortingDropdownOpen] = useState(false);
  const toggleSortingDropdown = () => setSortingDropdownOpen(!sortingDropdownOpen)
  const films = useSelector(state => state.films.films);
  setTimeout(async () => { document.querySelectorAll(".video-listing-card").forEach(element => { element.style.visibility = "visible" }) }, 1500)
  return <>

    <Row>
      <Colxx xxs="12">


        <Breadcrumb heading="films" match={match} style={{ display: "block" }} />

        <Row className='justify-content-between'>
          <Col xxs="12">
            <ButtonDropdown
              className="mr-1 mb-3"
              isOpen={sortingDropdownOpen}
              toggle={toggleSortingDropdown}
              style={{ display: "block" }}

            >
              <DropdownToggle caret size="xs" outline>
                <IntlMessages id="classement" />
              </DropdownToggle>

              <DropdownMenu>
                {sortingOptions.map((item) => (
                  <DropdownItem key={item.value} onClick={() => setSortingMethod(item.value)}>
                    <IntlMessages id={item.label} />
                  </DropdownItem>
                ))}
              </DropdownMenu>


            </ButtonDropdown>
          </Col>
          <Col className='text-right'>
          <p className='text-muted' >{films.length} films</p>
          </Col>
        </Row>

        <Separator className="mb-5" />

      </Colxx>
    </Row>

    <Row>
      <Colxx xxs="12" className="mb-4">

        {/* this is the video library  */}
        <ListPageListing
          items={sortFilms([...films])}
          displayMode={"imagelist"}
          selectedItems={[]}
          onCheckItem={() => { }}
          currentPage={1}
          totalPage={10}
          onContextMenuClick={() => { }}
          onChangePage={() => { }}


        />
      </Colxx>
    </Row>
  </>
};
export default Start;
