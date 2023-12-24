import React, {useEffect, useContext, useState} from 'react';
import {Breadcrumb, Button, Modal, ModalBody, ModalHeader, Row} from "reactstrap";
import {Colxx, Separator} from "../../../components/common/CustomBootstrap.jsx";
import {ImportBubbleTable} from "../../../containers/ui/ReactTableCards.jsx";
import {ImportContext} from "../../../providers/importsProvider.jsx";

const Import = ({match}) => {
    const imports = useContext(ImportContext).map(item => ({
        ignore: <i className="simple-icon-close p-0 m-0 w-10"/>, ...item
    }))


    const [currentFile, setCurrentFile] = useState()
    const [modalOpen, setModalOpen] = useState(false)
    const [formData, setFormData] = useState({
        title: "", actresses: ""
    })


    const fetchMetaDataApi = (tpdb_id) => {
        // get data from metadataapi
        // set to formData
    }

    const onClickSelect = (hash) => {
        imports.forEach(item => {
            if (item.hash === hash){
                setCurrentFile(item)
                setModalOpen(true)
            }
        })
    }

    const onClickDelete = (hash) => {
        // send ignore to server.
        console.log(`deleting ${hash}`);
    }

    const onSubmitForm = () => {
        // send form data to server
        // ensure filled.
        // close modal
    }

    const onFormUpdate = (e) => {
        setFormData(prevState => ({
            ...prevState,
            [e.target.attributes.name.value]: "poggers"
        }))

    }

    return (
        <>
            <Row>
                <Colxx xxs="12">
                    <h1>import</h1>
                    <Separator className="mb-5"/>
                </Colxx>
            </Row>
            <Row>
                <Colxx xxs="12" className="">
                    <ImportBubbleTable data={imports} onClickSelect={onClickSelect}
                                       onClickDelete={onClickDelete}/>
                    <Modal
                        isOpen={modalOpen}
                        size="lg"
                        toggle={() => setModalOpen(!modalOpen)}
                    >
                        <ModalHeader>Import Torrent</ModalHeader>
                        <ModalBody>
                            <label>Title:</label>
                            <input type="text" onChange={onFormUpdate} name="title" value={formData.title}/>
                            <Button>Submit </Button>
                        </ModalBody>
                    </Modal>

                </Colxx>
            </Row>

        </>
    )
}

export default Import