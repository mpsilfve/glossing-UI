'use strict';

/*
Main React component, renders ResultsTable and SideMenu componenets.

Props: 
    data - list of tokens with inputs and segmentations
    jobId
*/
class ResultsSection extends React.Component {

    constructor(props) {
        super(props);
        const {pages, sentence_boundaries} = this.computePages(props.data);
        // make a dictionary {key: list of indixes} and store it in state
        // but also make it updatable?
        const token_dictionary = this.makeTokenDictionary(props.data);

        // display segmentation and/or gloss?
        const includeSeg = 'preferred_segmentation' in props.data[0];
        const includeGloss = 'preferred_gloss' in props.data[0];
        
        this.state = {
            hasSeg: includeSeg,
            hasGloss: includeGloss,
            //  initial lower and upper bound from the rows 2D array
            lower_bound: pages[0].first_token,
            upper_bound: pages[0].last_sentence_end,
            pages: pages,
            currPage: 0,
            // below is a copy of input data
            data: [...props.data],
            token_dictionary: token_dictionary,
            modify_sentence: false,
            sentence_to_modify: {},
            sentence_boundaries: sentence_boundaries,
        };

        this.cancelSentenceResubmission = this.cancelSentenceResubmission.bind(this);
    }

    componentDidUpdate(prevProps, prevState) {
        // if the page changes, then hide the input box that allows sentence resubmission, 
        // since the sentence is no longer visible.
        if (prevState.upper_bound !== this.state.upper_bound) {
            this.setState({
                modify_sentence: false,
            });
        }

        // TODO: come back here for page legend!
        // console.log(this.state);
    }

    cancelSentenceResubmission() {
        this.setState({
            modify_sentence:false,
        });
    }

    computePages(data) {
        let pages = [];
        const token_list = data;
        const token_number = token_list.length;

        // The token index at the start of the current row
        let first_token = 0;
        let last_sentence_end = 0;
        let current_sentence_id = token_list[0].sentence_id;

        let sentence_boundaries = {}
        sentence_boundaries[token_list[0].sentence_id] = 0;

        const max_tokens_per_view = 50;
        for (let i = 0; i < token_number; i++) {
            // if a new sentence starts, update the current_sentence_id and sentence start and end
            if (current_sentence_id != token_list[i].sentence_id) {
                last_sentence_end = i - 1;
                current_sentence_id = token_list[i]["sentence_id"];
                sentence_boundaries[current_sentence_id] = i;
            }

            // when you exceed max tokens, make it last_sentence_end
            if (i == token_number - 1) {
                last_sentence_end = i;
            }

            // if we exceed max tokens per view or are at the end of the token list
            // 
            if (i - first_token + 1 >= max_tokens_per_view || i == token_number - 1) {
                // if sentence is too long, that just make it the end, otherwise just use
                // the sentence end
                last_sentence_end = first_token >= last_sentence_end ? i : last_sentence_end;
                // console.log(sentence_start);
                // console.log(`Start: ${first_token} and end ${last_sentence_end}`);
                let sentences_included = [];
                sentences_included.push(token_list[first_token].sentence_id);
                // in case if we deal with eaf file, add annotation id
                let annotations_included = [];
                if ('annotation_id' in token_list[first_token]) {
                    annotations_included.push(token_list[first_token]['annotation_id']);
                }
                // console.log(sentences_included);
                // include sentences that are within the current view
                for (let key in sentence_boundaries) {
                    if (sentence_boundaries[key] > first_token && sentence_boundaries[key] <= last_sentence_end) {
                        // keys in JavaScript are strings, and we need integers so use Number()
                        sentences_included.push(Number(key));
                        if ('annotation_id' in token_list[sentence_boundaries[key]]) {
                            annotations_included.push(token_list[sentence_boundaries[key]]['annotation_id']);
                        }
                    }           
                }
                if (('annotation_id' in token_list[first_token]) && (sentences_included.length != annotations_included.length)) {
                    throw new Error('Annotations are present but sentences included are not equal to annotations included!');
                }
                let page = {first_token, last_sentence_end, sentences_included, annotations_included};
                pages.push(page);
                first_token = last_sentence_end + 1;
            }
        }
        return {pages, sentence_boundaries};
    }

    // make a dictionary {key: list of indixes} which stores the
    // indices the input occurs in token_list.
    makeTokenDictionary(token_list) {
        const token_number = token_list.length;
        let dictionary = {};
        let current_token;
        for (let i = 0; i < token_number; i++) {
            current_token = token_list[i];
            if (!(current_token.input in dictionary)) {
                dictionary[current_token.input] = [i];
            } else {
                dictionary[current_token.input].push(i);
            }
        }
        return dictionary;
    }


    // Here is the page change method!
    handleClick(lower_b, upper_b, i) {
        this.setState({
            lower_bound: lower_b,
            upper_bound: upper_b,
            currPage: i
        });
        // console.log('The ResultsSection handleClick method was called.');
    }

    // update preferred segmentation and segmentation lists based on update mode and 
    // whether it is custom.
    updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode) {
        // create keys based on modelType value
        const modelKey = modelType;
        const modelPreferredKey = 'preferred_' + modelType;
        
        // TODO do something with the update mode
        const newData = [...this.state.data];
        console.log(`The index is ${index}`);
        newData[index][modelPreferredKey] = newPreferred;
        
        if (isCustom === true) {
            const same_token_index_list = this.state.token_dictionary[newData[index].input];

            if (update_mode === "only_this") {
                console.log("only this");
                newData[index][modelKey].push(newPreferred);
            } else if (update_mode === "all_after") {
                console.log("all after");
                for (let i = 0; i < same_token_index_list.length; i++) {
                    console.log(`The current index is ${same_token_index_list[i]}`)
                    if (same_token_index_list[i] > index) {
                        console.log(`This index is pushed ${same_token_index_list[i]}`)
                        newData[same_token_index_list[i]][modelKey].push(newPreferred);
                        newData[same_token_index_list[i]][modelPreferredKey] = newPreferred;
                    }
                }
            } else if (update_mode === "all") {
                console.log("all");
                for (let i = 0; i < same_token_index_list.length; i++) {
                    newData[same_token_index_list[i]][modelKey].push(newPreferred);
                    newData[same_token_index_list[i]][modelPreferredKey] = newPreferred;
                }
            } else {
                console.log("Wrong update mode!")
            }
        }

        this.setState({
            data: newData,
        });
    }

    determineSentenceBoundaries(sentence_id) {
        const sentence_start = this.state.sentence_boundaries[sentence_id];
        let sentence_end;

        if (this.state.sentence_boundaries[sentence_id + 1]) {

            sentence_end = this.state.sentence_boundaries[sentence_id + 1] - 1;
        } else {
            sentence_end = this.state.data.length - 1;
        }

        return [sentence_start, sentence_end];
    }

    retrieveSentenceToModify(sentence_id) {
        const sentence_boundary = this.determineSentenceBoundaries(sentence_id);
        const sentence_start = sentence_boundary[0];
        const sentence_end = sentence_boundary[1];

        console.log(`start ${sentence_start} and end ${sentence_end}`);
        let sentence = ""
        for (let i = sentence_start; i <= sentence_end; i++) {
            sentence = sentence.concat(this.state.data[i].input);
            if (i != sentence_end) {
                sentence = sentence.concat(" ");
            }
        }
        let sentence_to_modify = {sentence:sentence, sentence_id: sentence_id, annotation_id: null};
        if ('annotation_id' in this.state.data[sentence_start]) {
            sentence_to_modify.annotation_id = this.state.data[sentence_start].annotation_id;
        }

        this.setState({
            sentence_to_modify: sentence_to_modify,
            modify_sentence: true,
        });
    }

    async resubmitSentence(new_sentence) {
        // TODO make different requests depending on the eaf file or text
        this.setState({
            modify_sentence: false,
        });

        const inputText = new_sentence;
        const data = {
            text: inputText, 
            model: 'fairseq',
            nbest: this.state.data[0].nbest, 
            getSeg: this.state.hasSeg,
            getGloss: this.state.hasGloss
        };

        console.log(data);

        console.log(this.state.data);
        //  submit a new job and get a new job id (Changed: requesting batch job)
        const request = await requestData('/api/job/batch', data, 'POST');
        // wait for the job to finish and get the new data
        let status = {status:false};

        while(!status.status) {
            status = await requestData(`/api/job/${request.job_id}/batch`);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        const modified_sentence = await requestData(`/api/job/${request.job_id}/batch/download`);

        // exchange the tokens in data
        const sentence_id = this.state.sentence_to_modify.sentence_id;
        const sentence_boundary = this.determineSentenceBoundaries(sentence_id);
        const start = sentence_boundary[0];
        const end = sentence_boundary[1];
        // console.log(`start is ${start}, end is ${end}, modified sentence ${modified_sentence}`);

        // isolate the part before the modified sentence if it exists
        // then isolate the part after the modified sentence if it exists
        // then stich the before part with modified sentence and the after part.
        const before_modified = this.state.data.slice(0, start);
        let sentence_id_current = sentence_id;

        // modify sentence id's after modification in case if the modified sentence has been split into 2 or more sentences

        let updated_data = before_modified;


        console.log(`the annotation id of sentence to modify is ${this.state.sentence_to_modify.annotation_id}`)
        if (modified_sentence.length > 0) {
            console.log("i am inside the conditional")
            if (this.state.sentence_to_modify.annotation_id === null) {
                console.log("the annotation id is null")
                // if the iniput type originally was text, then recalculate sentence id, 
                // as a sentence can be split during resubmitting a sentence.
                let sentence_id_in_modified = modified_sentence[0].sentence_id;
                modified_sentence[0].sentence_id = sentence_id_current;
    
                for (let i = 1; i < modified_sentence.length; i++) {
                    if (modified_sentence[i].sentence_id != sentence_id_in_modified) {
                        sentence_id_current++;
                    }
                    sentence_id_in_modified = modified_sentence[i].sentence_id;
                    modified_sentence[i].sentence_id = sentence_id_current;
                    console.log(`${sentence_id_current} is current id and modified sentence has id ${modified_sentence[i].sentence_id}`);
                }
            } else {
                console.log("I am inside else")
                // if the input type origianlly was an eaf file, then simply assign the same sentence id 
                // and annotation id to the entire resubmitted output as originally, as we do not allow
                // changing annotation id for the resubmitted chunk.
                const original_sentence_id = this.state.sentence_to_modify.sentence_id;
                const original_annotation_id = this.state.sentence_to_modify.annotation_id;
                console.log(`original annotation id is ${original_annotation_id}`)
                console.log(`original sentence id ${original_sentence_id}`)
                console.log(original_sentence_id);
                for (let i = 0; i < modified_sentence.length; i++) {
                    modified_sentence[i].sentence_id = original_sentence_id;
                    modified_sentence[i].annotation_id = original_annotation_id;
                }
            }


            updated_data = updated_data.concat(modified_sentence);
        }

        sentence_id_current++;

        console.log(`the length of data is ${this.state.data.length} and the end is on ${end}`);
        if (end + 1 !== this.state.data.length) {
            const after_modified = this.state.data.slice(end + 1, this.state.data.length);

            let previous_id = after_modified[0].sentence_id;
            after_modified[0].sentence_id = sentence_id_current;

            for (let i = 1; i < after_modified.length; i++) {
                if (after_modified[i].sentence_id != previous_id) {
                    sentence_id_current++;
                }
                previous_id = after_modified[i].sentence_id;
                after_modified[i].sentence_id = sentence_id_current;
            }
            updated_data = updated_data.concat(after_modified);
        }
    
        // console.log(`new data length is ${updated_data.length}`)
        // for (let i=0; i< updated_data.length; i++) {
        //     console.log(updated_data[i].annotation_id);
        // }

        
        // update the state

        // need to update the state in such a way so that the results table
        // shows at the panel with the updated sentence

        const {pages, sentence_boundaries} = this.computePages(updated_data);
        // make a dictionary {key: list of indixes} and store it in state
        // but also make it updatable?
        const token_dictionary = this.makeTokenDictionary(updated_data);

        
        // determine the lower and upper bounds of the page on which the modified setences appears
        let lower_bound;
        let upper_bound;

        for (let k = 0; k < pages.length; k++) {
            if (sentence_id in pages[k].sentences_included) {
                lower_bound = pages[k].first_token;
                upper_bound = pages[k].last_sentence_end;
                break;
            }
        }

        this.setState({
            lower_bound: lower_bound,
            upper_bound: upper_bound,
            pages: pages,
            data: updated_data,
            token_dictionary: token_dictionary,
            modify_sentence: false,
            sentence_to_modify: {},
            sentence_boundaries: sentence_boundaries,
        });
    }

    async handleSave(filename, format, saveGloss, saveSeg) {
        console.log(this.state.data);

        // if the format is text, save a file of preferred segmentations. If it's an EAF, convert and then save
        if (format === 'txt') {
            // generate a string representing the preferred segmentations of all the tokens. Sentences separated by lines.
            let seg_tokens = [];
            let gloss_tokens = [];
            let curr_sentence = -1;

            for (let i=0; i < this.state.data.length; i++) {
                let curr_token = this.state.data[i];

                if (curr_token['sentence_id'] > curr_sentence) {
                    seg_tokens.push([]);
                    gloss_tokens.push([]);
                    curr_sentence++;
                }

                seg_tokens[seg_tokens.length - 1].push(curr_token['preferred_segmentation']);
                gloss_tokens[gloss_tokens.length - 1].push(curr_token['preferred_gloss']);
            }

            // construct a string from the two list of lists, depending on preferences
            let output_string = '';
            for (let i=0; i<seg_tokens.length; i++) { 
                if (saveSeg) {
                    output_string += seg_tokens[i].join(' ') + '\n';
                }
                if (saveGloss) {
                    output_string += gloss_tokens[i].join(' ') + '\n';
                }
                if (saveSeg && saveGloss && i < seg_tokens.length - 1) {
                    output_string += '\n';
                }
            }
            // let output_string = '';
            // for (const sent of output_tokens) {
            //     output_string += sent.join(' ') + '\n';
            // }

            console.log(output_string);

            // download text as a blob
            let output_blob = new Blob([output_string], {type: "text/plain;charset=utf-8"});
            var link = document.createElement('a');
            link.download = filename + '.' + format;
            link.href = window.URL.createObjectURL(output_blob);
            link.click();
        } else {
            let model_type = 'both';
            if (!saveGloss) {
                model_type = 'segmentation';
            } else if (!saveSeg) {
                model_type = 'gloss';
            }

            const data = {id: this.props.jobId, tokens: this.state.data, models: model_type};
            console.log(data);

            // submit an API request
            const result = await requestData('/api/job/convert', data, 'POST');
            console.log(result);

            // wait for the job to finish and get the new data
            let status = {status:false};

            while(!status.status) {
                status = await requestData(`/api/job/${this.props.jobId}/get_eaf_file`);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            console.log(status);
            let save_text = status.written_elan;

            // download text as a blob
            let output_blob = new Blob([save_text], {type: "text/plain;charset=utf-8"});
            var link = document.createElement('a');
            link.download = filename + '.' + format;
            link.href = window.URL.createObjectURL(output_blob);
            link.click();
        }
        
    }

    render() {
        return (
            <div>
                {this.state.modify_sentence && (<ResubmitSentenceSection 
                        sentence={this.state.sentence_to_modify.sentence}
                        onSubmit={(new_sentence) => {this.resubmitSentence(new_sentence)}}
                        cancelSentenceResubmission={this.cancelSentenceResubmission}
                    />)}
                <div id="completed_message">
                    <SideMenu 
                        data={this.state.pages}
                        hasSeg={this.state.hasSeg}
                        hasGloss={this.state.hasGloss}
                        currPage={this.state.currPage}
                        onClick={(lower_b, upper_b, i) => this.handleClick(lower_b, upper_b, i)}
                        onRetrieveSentence={(sentence_id) => {this.retrieveSentenceToModify(sentence_id)}}
                        handleSave={(filename, format, saveGloss, saveSeg) => this.handleSave(filename, format, saveGloss, saveSeg)}
                    />
                    <DynamicResultsTable 
                        data={this.state.data} 
                        lower_bound={this.state.lower_bound} 
                        upper_bound={this.state.upper_bound}
                        hasSeg={this.state.hasSeg}
                        hasGloss={this.state.hasGloss}
                        updatePreferredSegmentation = {
                            (index, modelType, newPreferred, isCustom, update_mode) => 
                                this.updatePreferredSegmentation(index, modelType, newPreferred, isCustom, update_mode)
                        }
                    />
                </div>
                <div id="completed_message">
                    <PageNav 
                        data={this.state.pages}
                        currPage={this.state.currPage}
                        onClick={(lower_b, upper_b, i) => this.handleClick(lower_b, upper_b, i)}
                    /> 
                </div>    
            </div>
        )
    }
}

// TODO fix bug in sentence resubmission

// add sentence indexing
// page table - show number of sentences that fit into 100 tokens
// and do not cut sentence in the middle
// below page add buttons for sentences
// when you hove over these buttons, the sentence cells will
// will highlight.
// when you click on sentence edit button, a window with input sentence will show up
// above the results table with "resubmit" button
// the whole table will then refresh
// how should i hold the data in a JSON object then?
// as token id, you can use sentence id and index within a sentence

