'use strict';

class ResubmitSentenceSection extends React.Component {
    constructor(props){
        super(props)
        this.state = {
          value: this.props.sentence,
        //   set update_mode to default checked radio button value
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    // called upon sentence prop update
    componentDidUpdate(prevProps) {
        if (prevProps.sentence !== this.props.sentence) {
            this.setState({
                value: this.props.sentence,
            });
        }
    }

    handleChange(event) {
        this.setState({
            value: event.target.value,
        });
    }

    handleSubmit(event) {
        this.props.onSubmit(this.state.value);
        this.setState({
            value: '',
        });
        event.preventDefault();
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit} className="form">
                <input 
                    type="text" 
                    value={this.state.value}
                    onChange={this.handleChange}
                    className="user_input" 
                    id="modified_sentence_input"
                    required>
                </input>
                <input type="submit" 
                        className="job_buttons"
                        value="Re-submit sentence">
                </input>
                <button className="job_buttons"
                        onClick={this.props.cancelSentenceResubmission}>
                            Cancel
                </button>
            </form>
        );

    }
}