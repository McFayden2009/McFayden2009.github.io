const MIN_SPEED = 4
const MAX_SPEED = 5

function randomNumber(min, max) {
  return Math.random() * (max - min) + min
}

class Blob {
  constructor(el) {
    this.el = el
    const boundingRect = this.el.getBoundingClientRect()
    this.size = boundingRect.width
    this.initialX = randomNumber(0, window.innerWidth - this.size)
    this.initialY = randomNumber(0, window.innerHeight - this.size)
    this.el.style.top = `${this.initialY}px`
    this.el.style.left = `${this.initialX}px`
    this.vx =
      randomNumber(MIN_SPEED, MAX_SPEED) * (Math.random() > 0.5 ? 1 : -1)
    this.vy =
      randomNumber(MIN_SPEED, MAX_SPEED) * (Math.random() > 0.5 ? 1 : -1)
    this.x = this.initialX
    this.y = this.initialY
  }

  update() {
    this.x += this.vx
    this.y += this.vy
    if (this.x >= window.innerWidth - this.size) {
      this.x = window.innerWidth - this.size
      this.vx *= -1
    }
    if (this.y >= window.innerHeight - this.size) {
      this.y = window.innerHeight - this.size
      this.vy *= -1
    }
    if (this.x <= 0) {
      this.x = 0
      this.vx *= -1
    }
    if (this.y <= 0) {
      this.y = 0
      this.vy *= -1
    }
  }

  move() {
    this.el.style.transform = `translate(${this.x - this.initialX}px, ${
      this.y - this.initialY
    }px)`
  }
}

function initBlobs() {
  const blobEls = document.querySelectorAll('.bouncing-blob')
  const blobs = Array.from(blobEls).map((blobEl) => new Blob(blobEl))

  function update() {
    requestAnimationFrame(update)
    blobs.forEach((blob) => {
      blob.update()
      blob.move()
    })
  }

  requestAnimationFrame(update)
}

initBlobs()


/**
---------------------------
RANDOM NAME JS CODE BELLOW 
---------------------------
**/



import React from "https://esm.sh/react";
import ReactDOM from "https://esm.sh/react-dom";
import PropTypes from "https://esm.sh/prop-types";
import { jsx as _jsx, jsxs as _jsxs } from "https://esm.sh/react/jsx-runtime";

class RandomPicker extends React.PureComponent {
  constructor() {
    super();
    this.state = {
      isRunning: false,
      currentChoice: ''
    };
    this.interval = null;
    this.intervalDuration = 75;
    this.duration = 1000;
    this.start = this.start.bind(this);
    this.stop = this.stop.bind(this);
    this.pickChoice = this.pickChoice.bind(this);
    this.setChoice = this.setChoice.bind(this);
  }
  start() {
    clearInterval(this.interval);
    this.interval = setInterval(this.setChoice, this.intervalDuration);
    this.setState({
      isRunning: true
    });
    setTimeout(() => {
      if (this.state.isRunning) {
        this.stop();
      }
    }, this.duration);
  }
  stop() {
    clearInterval(this.interval);
    this.setState({
      isRunning: false
    });
  }
  pickChoice() {
    const { items } = this.props;
    const choice = items[Math.floor(Math.random() * items.length)];
    return choice;
  }
  setChoice() {
    this.setState({
      currentChoice: this.pickChoice()
    });
  }
  render() {
    const { isRunning, currentChoice } = this.state;
    return /*#__PURE__*/_jsxs("div", {
      className: "RandomPicker",
      children: [
        /*#__PURE__*/_jsx(RandomPickerChoice, { choice: currentChoice }),
        /*#__PURE__*/_jsx(RandomPickerControls, {
          isRunning: isRunning,
          hasChoice: currentChoice.trim().length > 0,
          start: this.start,
          stop: this.stop
        })
      ]
    });
  }
}

RandomPicker.propTypes = {
  items: PropTypes.array,
  duration: PropTypes.number
};

class RandomPickerChoice extends React.PureComponent {
  render() {
    const { choice } = this.props;
    const content = choice.trim().length > 0 ? choice : '?';
    return /*#__PURE__*/_jsx("div", {
      className: "RandomPicker__choice",
      children: /*#__PURE__*/_jsx("span", {
        className: "RandomPicker__choiceItem",
        children: content
      })
    });
  }
}

RandomPickerChoice.propTypes = {
  choice: PropTypes.string
};

class RandomPickerControls extends React.PureComponent {
  render() {
    const { isRunning, hasChoice, start, stop } = this.props;
    return /*#__PURE__*/_jsx("div", {
      className: "RandomPicker__controls",
      children: /*#__PURE__*/_jsx("button", {
        className: `RandomPicker__button ${isRunning && 'RandomPicker__button--stop'}`,
        onClick: isRunning ? stop : start,
        children: isRunning ? 'stop' : 'start'
      })
    });
  }
}

RandomPickerControls.propTypes = {
  isRunning: PropTypes.bool,
  hasChoice: PropTypes.bool,
  start: PropTypes.func,
  stop: PropTypes.func
};

const namesList = ['Tayden', 'Amy', 'Meia'];
ReactDOM.render( /*#__PURE__*/_jsx(RandomPicker, { items: namesList }), document.getElementById('random-picker'));