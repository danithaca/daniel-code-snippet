/*
 * Copyright 2004-2005 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package net.sf.jml.protocol.incoming;

import net.sf.jml.MsnProtocol;
import net.sf.jml.protocol.MsnIncomingMessage;

/**
 * OutgoingUUX's response.
 * <p>
 * Supported Protocol: MSNP11
 * <p>
 * Syntax: UUX trId msgLen\r\n content
 * 
 * @author Roger Chen
 */
public class IncomingUUX extends MsnIncomingMessage {

    public IncomingUUX(MsnProtocol protocol) {
        super(protocol);
    }

    @Override
	protected boolean isSupportChunkData() {
        return true;
    }

}