import React, { useState, useContext, useEffect } from 'react';
import {
    Row,
    Card,
    CardBody,
    Button,
    CardSubtitle,
    CardText,
    CardImg,
} from 'reactstrap';
import { NavLink } from 'react-router-dom';
import Breadcrumb from '../../../containers/navs/Breadcrumb';
import {Colxx, Separator} from '../../../components/common/CustomBootstrap';
import SingleLightbox from '../../../components/pages/SingleLightbox';
import {FilmContext} from "../../../providers/filmsProvider.jsx";

const ActressDetail = ({ match, actress }) => {

    const api_key = "waTXQgn2YpJriGIwrJtn9v7ibRqakf1yHyROuPxE244e319b"

    const films = useContext(FilmContext).filter(film => {return film.actresses.includes(actress)})

    const [averageRating, setAverageRating] = useState(0.0)

    const [birthday, setBirthday] = useState(undefined)
    const [ethnicity, setEthnicity] = useState(undefined)
    const [nationality, setNationality] = useState(undefined)
    const [height, setHeight] = useState(undefined)
    const [about, setAbout] = useState(undefined)
    const [imageUrl, setImageUrl] = useState(undefined)
    const [hairColor, setHairColor] = useState(undefined)

    const [loading, setLoading] = useState(true)
    useEffect(() => {
        fetch(`https://api.metadataapi.net/performers?q=${actress}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${api_key}`
            }
        })
            .then(response => response.json())
            .then(data => {
                fetch(`https://api.metadataapi.net/performers/${data.data[0].id}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${api_key}`
                    }
                }).then(response => response.json())
                    .then(data => {
                        const img = new Image()
                        img.src = data.data?.face
                        setImageUrl(data.data?.face)
                        setBirthday(data.data?.extras?.birthday)
                        setEthnicity(data.data?.extras?.ethnicity)
                        setNationality(data.data?.extras?.nationality)
                        setAbout(data.data?.bio)
                        setHeight(data.data?.extras?.height)
                        setHairColor(data.data?.extras?.hair_colour)
                        const nonZeroAverageFilms = films.filter( film => film.rating.average !== 0)
                        const totalSumAverages = nonZeroAverageFilms.reduce((sum, film) => sum + film.rating.average, 0)
                        setAverageRating(nonZeroAverageFilms > 0 ? totalSumAverages / nonZeroAverageFilms.length : 0 )
                        img.onload = () => {setLoading(false)}
                        img.onerror = () => {setLoading(false)}
                    })

            })
    }, []);



    if (loading){
        return (
            <>
                <div className="loading"> </div>
            </>
        )
    }

    return (
        <>
            <Row>
                <Colxx xxs="12">
                    <Breadcrumb heading={actress} match={match} />
                    <Separator className="mb-5" />
                </Colxx>
            </Row>
            <Row>
                <Colxx xxs="12" className="mb-4">


                    <Row>
                        <Colxx xxs="12" lg="3" className="mb-4 col-left">
                            <Card className="mb-4 h-100">

                                <CardImg
                                    style={{objectFit: "cover", objectPosition: "left top"}}
                                    className="card-img-top h-100"
                                    src={imageUrl}

                                />

                                <CardBody>
                                    {
                                        about && (
                                            <>
                                                <p className="text-muted text-small mb-2">
                                                    about
                                                </p>
                                                <p className="mb-3">
                                                    {about}
                                                </p>
                                            </>
                                        )
                                    }

                                    {
                                        nationality && (
                                        <>
                                            <p className="text-muted text-small mb-2">
                                                nationality
                                            </p>
                                            <p className="mb-3">{nationality}</p>

                                        </>

                                        )

                                    }

                                    {
                                        height && (
                                            <>
                                                <p className="text-muted text-small mb-2">
                                                    height
                                                </p>
                                                <p className="mb-3">{height}</p>

                                            </>

                                        )

                                    }

                                    {
                                        birthday && (
                                            <>
                                                <p className="text-muted text-small mb-2">
                                                    birthday
                                                </p>
                                                <p className="mb-3">{birthday}</p>

                                            </>

                                        )

                                    }
                                    {
                                        hairColor && (
                                            <>
                                                <p className="text-muted text-small mb-2">
                                                    hair color
                                                </p>
                                                <p className="mb-3">{hairColor}</p>

                                            </>

                                        )

                                    }

                                    <div className="social-icons">
                                        <ul className="list-unstyled list-inline">
                                            <li className="list-inline-item">
                                                <NavLink to="#" location={{}}>
                                                    <i className="simple-icon-social-youtube" />
                                                </NavLink>
                                            </li>
                                        </ul>
                                    </div>
                                </CardBody>
                            </Card>

                        </Colxx>

                        <Colxx xxs="12" lg="9" className="mb-4 col-right">
                            <Row>
                                {films?.map((film) => {
                                    return (
                                        <Colxx
                                            xxs="12"
                                            lg="6"
                                            xl="4"
                                            className="mb-4"
                                            key={`product_${film.uuid}`}
                                        >
                                            <Card>
                                                <div className="position-relative">
                                                    <NavLink
                                                        to="#"
                                                        location={{}}
                                                        className="w-40 w-sm-100"
                                                    >
                                                        <CardImg
                                                            top
                                                            alt={film.title}
                                                            src={import.meta.env.DEV ? `/assets/img/films/${film.uuid}.png` : `/api/thumbnail?uuid=${film.uuid}`}
                                                        />
                                                    </NavLink>
                                                </div>
                                                <CardBody>
                                                    <NavLink
                                                        to="#"
                                                        location={{}}
                                                        className="w-40 w-sm-100"
                                                    >
                                                        <CardSubtitle>{film.title}</CardSubtitle>
                                                    </NavLink>
                                                    <CardText className="text-muted text-small mb-0 font-weight-light">
                                                        {film.date_added}
                                                    </CardText>
                                                </CardBody>
                                            </Card>
                                        </Colxx>
                                    );
                                })}
                            </Row>
                        </Colxx>
                    </Row>

                </Colxx>
            </Row>
        </>
    );
};
export default ActressDetail;



