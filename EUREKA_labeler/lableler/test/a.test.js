//var assert = require('assert');
import assert from 'assert';
import { soy } from '../src/util/Util'
describe('just try', function () {
    describe('soy test', function () {
        it('should return soy', function () {
            assert.equal(soy(''), 'soy');
        })
    })
});