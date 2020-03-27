import { formsForet} from './forms/foret'
import { formsPeuplement} from './forms/peuplement'
import { formsDegat } from './forms/degat'
import { formsCommentaires } from './forms/commentaires.js'
import { formsValidation } from './forms/validation'


import { sessionsForet } from './sessions/foret'
import { sessionsPeuplement } from './sessions/peuplement'
import { sessionsDegat } from './sessions/degat'
import { sessionsCommentaires } from './sessions/commentaires'
import { sessionsValidation } from './sessions/validation'

import { config } from './declarations.js'

import ConfigDeclaration from './config-declaration'

const forms = {
    ...formsForet,
    ...formsPeuplement,
    ...formsDegat,
    ...formsCommentaires,
    ...formsValidation    }

const sessions = {
    ...sessionsForet,
    ...sessionsPeuplement,
    ...sessionsDegat,
    ...sessionsCommentaires,
    ...sessionsValidation    
}

const configDeclaration = new ConfigDeclaration(config, sessions, forms);

export { configDeclaration }
